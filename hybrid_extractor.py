"""
Hybrid extractor combining API and browser automation strategies.

This extractor tries multiple methods to extract conversation data:
1. API-based extraction (fastest, most reliable)
2. Browser automation with Playwright (fallback)
3. DOM scraping (last resort)
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from loguru import logger
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from claude_extractor.models import (
    Artifact,
    ArtifactType,
    Branch,
    Conversation,
    ConversationMetadata,
    ConversationStatistics,
    Message,
    MessageRole,
    ToolCall,
    ToolCallStatus,
)


class ExtractionError(Exception):
    """Base exception for extraction errors."""
    pass


class AuthenticationError(ExtractionError):
    """Authentication failed."""
    pass


class HybridExtractor:
    """
    Hybrid extraction strategy combining API and browser automation.
    
    This extractor intelligently falls back through multiple strategies
    to ensure reliable data extraction.
    """
    
    def __init__(
        self,
        auth_cookie: Optional[str] = None,
        timeout: int = 60,
        include_thinking: bool = True,
        verbose: bool = False,
    ):
        """
        Initialize hybrid extractor.
        
        Args:
            auth_cookie: Claude.ai session cookie
            timeout: Request timeout in seconds
            include_thinking: Include Claude's thinking process
            verbose: Enable verbose logging
        """
        self.auth_cookie = auth_cookie
        self.timeout = timeout
        self.include_thinking = include_thinking
        self.verbose = verbose
        
        if verbose:
            logger.setLevel("DEBUG")
    
    def extract(self, url: str) -> Conversation:
        """
        Extract conversation from URL.
        
        Args:
            url: Claude conversation URL
        
        Returns:
            Extracted conversation data
        
        Raises:
            ExtractionError: If extraction fails with all strategies
        """
        conversation_id = self._parse_url(url)
        logger.info(f"Extracting conversation: {conversation_id}")
        
        # Try extraction strategies in order
        strategies = [
            ("API", self._extract_via_api),
            ("Browser", self._extract_via_browser),
        ]
        
        last_error = None
        for strategy_name, strategy_func in strategies:
            try:
                logger.info(f"Trying {strategy_name} extraction...")
                conversation = asyncio.run(strategy_func(url, conversation_id))
                logger.success(f"Successfully extracted via {strategy_name}")
                return conversation
            except Exception as e:
                logger.warning(f"{strategy_name} extraction failed: {e}")
                last_error = e
                continue
        
        # All strategies failed
        raise ExtractionError(
            f"All extraction strategies failed. Last error: {last_error}"
        )
    
    async def _extract_via_api(
        self,
        url: str,
        conversation_id: str,
    ) -> Conversation:
        """
        Extract using Claude.ai API (if accessible).
        
        Note: This requires reverse-engineering Claude's internal API,
        which may not be publicly documented. This is a placeholder
        for the actual implementation.
        """
        # TODO: Implement actual API extraction once endpoints are identified
        # This would require analyzing Claude.ai's network requests
        raise NotImplementedError("API extraction not yet implemented")
    
    async def _extract_via_browser(
        self,
        url: str,
        conversation_id: str,
    ) -> Conversation:
        """
        Extract using browser automation with Playwright.
        
        This method:
        1. Launches a browser
        2. Navigates to the conversation
        3. Injects authentication
        4. Extracts DOM content
        5. Parses into structured data
        """
        logger.debug("Launching browser...")
        
        async with async_playwright() as p:
            # Launch browser (headless by default)
            browser = await p.chromium.launch(headless=not self.verbose)
            context = await browser.new_context()
            
            # Set authentication cookie if provided
            if self.auth_cookie:
                await context.add_cookies([{
                    "name": "sessionKey",
                    "value": self.auth_cookie,
                    "domain": ".claude.ai",
                    "path": "/",
                }])
            
            page = await context.new_page()
            
            try:
                # Navigate to conversation
                logger.debug(f"Navigating to {url}")
                await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
                
                # Wait for conversation to load
                await page.wait_for_selector('[data-testid="chat-message"]', timeout=30000)
                
                # Extract data
                conversation_data = await self._extract_from_page(page, conversation_id)
                
                # Parse into Conversation object
                conversation = await self._parse_conversation(conversation_data, url)
                
                return conversation
                
            finally:
                await browser.close()
    
    async def _extract_from_page(
        self,
        page,
        conversation_id: str,
    ) -> Dict[str, Any]:
        """
        Extract conversation data from loaded page.
        
        Uses JavaScript to parse DOM and extract structured data.
        """
        logger.debug("Extracting data from page DOM...")
        
        # Inject extraction script
        extraction_script = """
        () => {
            const data = {
                title: document.title || 'Untitled Conversation',
                messages: [],
                artifacts: [],
                metadata: {},
            };
            
            // Extract messages
            const messageElements = document.querySelectorAll('[data-testid="chat-message"]');
            messageElements.forEach((msgEl, index) => {
                const roleEl = msgEl.querySelector('[data-role]');
                const role = roleEl ? roleEl.getAttribute('data-role') : 'unknown';
                
                const contentEl = msgEl.querySelector('.prose');
                const content = contentEl ? contentEl.innerText : '';
                
                const timestampEl = msgEl.querySelector('[data-timestamp]');
                const timestamp = timestampEl ? timestampEl.getAttribute('data-timestamp') : new Date().toISOString();
                
                data.messages.push({
                    id: `msg_${index}`,
                    role: role,
                    content: content,
                    timestamp: timestamp,
                });
            });
            
            // Extract artifacts (simplified)
            const artifactElements = document.querySelectorAll('[data-artifact-id]');
            artifactElements.forEach((artEl) => {
                const artifactId = artEl.getAttribute('data-artifact-id');
                const artifactType = artEl.getAttribute('data-artifact-type') || 'code';
                const content = artEl.querySelector('code, pre')?.innerText || '';
                
                data.artifacts.push({
                    id: artifactId,
                    type: artifactType,
                    content: content,
                });
            });
            
            return data;
        }
        """
        
        try:
            data = await page.evaluate(extraction_script)
            logger.debug(f"Extracted {len(data.get('messages', []))} messages")
            return data
        except Exception as e:
            logger.error(f"Failed to extract data from page: {e}")
            raise ExtractionError(f"DOM extraction failed: {e}")
    
    async def _parse_conversation(
        self,
        data: Dict[str, Any],
        url: str,
    ) -> Conversation:
        """
        Parse extracted data into Conversation model.
        
        Args:
            data: Raw extracted data
            url: Conversation URL
        
        Returns:
            Parsed Conversation object
        """
        logger.debug("Parsing extracted data...")
        
        conversation_id = self._parse_url(url)
        
        # Parse messages
        messages = []
        for msg_data in data.get("messages", []):
            try:
                message = Message(
                    id=msg_data.get("id", f"msg_{len(messages)}"),
                    role=MessageRole(msg_data.get("role", "user")),
                    content=msg_data.get("content", ""),
                    timestamp=datetime.fromisoformat(
                        msg_data.get("timestamp", datetime.now().isoformat())
                    ),
                    parent_id=msg_data.get("parent_id"),
                    branch_id=msg_data.get("branch_id", "main"),
                    tokens=msg_data.get("tokens"),
                    thinking_content=msg_data.get("thinking_content") if self.include_thinking else None,
                )
                messages.append(message)
            except Exception as e:
                logger.warning(f"Failed to parse message: {e}")
                continue
        
        # Parse artifacts
        artifacts = []
        for art_data in data.get("artifacts", []):
            try:
                artifact = Artifact(
                    id=art_data.get("id", f"art_{len(artifacts)}"),
                    type=ArtifactType(art_data.get("type", "code")),
                    title=art_data.get("title", "Untitled"),
                    content=art_data.get("content", ""),
                    language=art_data.get("language"),
                    created_in_message=art_data.get("created_in_message", ""),
                    created_at=datetime.now(),
                )
                artifacts.append(artifact)
            except Exception as e:
                logger.warning(f"Failed to parse artifact: {e}")
                continue
        
        # Calculate statistics
        stats = ConversationStatistics(
            total_messages=len(messages),
            user_messages=len([m for m in messages if m.role == MessageRole.USER]),
            assistant_messages=len([m for m in messages if m.role == MessageRole.ASSISTANT]),
            artifact_count=len(artifacts),
            total_tokens=sum(m.tokens or 0 for m in messages),
        )
        
        # Create metadata
        metadata = ConversationMetadata(
            id=conversation_id,
            url=url,
            title=data.get("title", "Untitled Conversation"),
            created_at=messages[0].timestamp if messages else datetime.now(),
            updated_at=messages[-1].timestamp if messages else datetime.now(),
            model=data.get("model", "unknown"),
        )
        
        # Create conversation
        conversation = Conversation(
            metadata=metadata,
            messages=messages,
            artifacts=artifacts,
            branches=[Branch(
                id="main",
                parent_message_id="",
                created_at=datetime.now(),
                is_active=True,
                message_ids=[m.id for m in messages],
            )],
            tool_calls=[],
            statistics=stats,
            extraction_metadata={
                "extracted_at": datetime.now().isoformat(),
                "extractor_version": "0.1.0",
                "method": "browser_automation",
            },
        )
        
        logger.success(f"Parsed conversation: {stats.total_messages} messages, {stats.artifact_count} artifacts")
        
        return conversation
    
    def _parse_url(self, url: str) -> str:
        """Extract conversation ID from URL."""
        # Handle both formats:
        # https://claude.ai/chat/CONVERSATION_ID
        # https://claude.ai/chat/CONVERSATION_ID?...
        parsed = urlparse(url)
        path_parts = parsed.path.split("/")
        
        # Find 'chat' in path and get next part
        try:
            chat_index = path_parts.index("chat")
            conversation_id = path_parts[chat_index + 1]
            return conversation_id
        except (ValueError, IndexError):
            raise ExtractionError(f"Invalid conversation URL: {url}")
