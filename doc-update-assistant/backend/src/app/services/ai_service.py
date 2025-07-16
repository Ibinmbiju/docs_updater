# AI service
"""AI service for generating documentation update suggestions."""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from openai import OpenAI

from ..models.document import DocumentSection, DocumentType
from ..models.suggestion import SuggestionType, UpdateSuggestion
from ..services.diff_service import DiffService
from ..utils.exceptions import AIServiceError
from ..config import settings


class AIService:
    """Enhanced AI service for OpenAI Agents SDK documentation updates. Handles all AI-based suggestion generation and context analysis."""
    
    def __init__(self) -> None:
        """Initialize the AI service, ensuring the OpenAI API key is set and the client is ready."""
        api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise AIServiceError(
                "OpenAI API key is missing. Please set OPENAI_API_KEY in your environment or .env file. "
                "Suggestions cannot be generated without it."
            )
        self.client = OpenAI(api_key=api_key, timeout=30)
        self.diff_service = DiffService()
        
    async def generate_suggestions(
        self, 
        query: str, 
        relevant_sections: list[DocumentSection]
    ) -> list[UpdateSuggestion]:
        """Generate update suggestions based on query and relevant sections. Optimized for speed with parallel processing."""
        import asyncio
        
        # Skip context analysis for speed - derive context from query directly
        change_context = self._quick_analyze_query_context(query)
        
        # Parallelize suggestion generation for all relevant sections
        tasks = [
            self._generate_section_suggestion_fast(query, section, change_context)
            for section in relevant_sections
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        suggestions = [s for s in results if s and not isinstance(s, Exception)]
        return suggestions
    
    def _quick_analyze_query_context(self, query: str) -> dict[str, Any]:
        """Quick local analysis of query context without API calls for speed."""
        query_lower = query.lower()
        
        # Quick keyword-based analysis
        change_type = "update"
        if any(word in query_lower for word in ["deprecat", "remove", "old"]):
            change_type = "deprecation"
        elif any(word in query_lower for word in ["add", "new", "introduce"]):
            change_type = "new_feature"
        elif any(word in query_lower for word in ["api", "endpoint", "method"]):
            change_type = "api_change"
        
        # Quick concept detection
        affected_concepts = []
        concept_map = {
            "agent": ["agent", "llm"],
            "handoff": ["handoff", "delegate", "transfer"],
            "tool": ["tool", "function", "call"],
            "guardrail": ["guardrail", "validation", "check"],
            "runner": ["runner", "execute", "run"]
        }
        
        for concept, keywords in concept_map.items():
            if any(keyword in query_lower for keyword in keywords):
                affected_concepts.append(concept)
        
        return {
            "change_type": change_type,
            "affected_concepts": affected_concepts,
            "urgency": "medium",
            "scope": "minor",
            "keywords": query_lower.split(),
            "summary": f"Quick analysis: {change_type} for {', '.join(affected_concepts) if affected_concepts else 'general'}"
        }

    def _get_query_context_system_prompt(self) -> str:
        """Return the system prompt for analyzing the query context."""
        return (
            "You are an expert in analyzing documentation update requests for the OpenAI Agents SDK.\n"
            "Analyze the user's query and identify:\n"
            "1. What specific features/concepts are being changed\n"
            "2. The type of change (deprecation, new feature, API change, etc.)\n"
            "3. What sections of documentation might be affected\n"
            "4. The urgency and scope of the changes\n"
            "Return a JSON object with your analysis."
        )

    def _get_query_context_user_prompt(self, query: str) -> str:
        """Return the user prompt for analyzing the query context."""
        return f"""
        Analyze this documentation update request for OpenAI Agents SDK:
        Query: {query}
        Provide analysis in this JSON format:
        {{
            "change_type": "deprecation|new_feature|api_change|clarification|bug_fix",
            "affected_concepts": ["agent", "handoff", "guardrail", "tool", "runner"],
            "urgency": "high|medium|low",
            "scope": "major|minor|patch",
            "keywords": ["list", "of", "relevant", "terms"],
            "summary": "Brief summary of what needs to be changed"
        }}
        """
    
    async def _generate_section_suggestion(
        self, 
        query: str, 
        section: DocumentSection,
        change_context: dict[str, Any]
    ) -> UpdateSuggestion | None:
        """Generate a suggestion for a specific section using the AI model and context."""
        try:
            system_prompt = self._get_specialized_system_prompt(section, change_context)
            user_prompt = self._get_specialized_user_prompt(query, section, change_context)
            response = await self._call_openai_api(system_prompt, user_prompt)
            if not response:
                return None
            suggestion_data = self._parse_ai_response(response)
            if not suggestion_data.get('should_update', False):
                return None
            original_content = section.content
            suggested_content = suggestion_data.get('suggested_content', '')
            if not suggested_content or suggested_content == original_content:
                return None
            diff_hunks = self.diff_service.generate_diff_hunks(
                original_content, 
                suggested_content
            )
            suggestion_type = self._determine_suggestion_type(
                suggestion_data, change_context
            )
            return UpdateSuggestion(
                id=self._generate_suggestion_id(),
                document_id=section.file_path,
                section_id=section.id,
                title=suggestion_data.get('title', f"Update {section.title}"),
                description=suggestion_data.get('description', ''),
                diff_hunks=diff_hunks,
                original_content=original_content,
                suggested_content=suggested_content,
                suggestion_type=suggestion_type,
                confidence_score=suggestion_data.get('confidence', 0.0),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                reasoning=suggestion_data.get('reasoning', ''),
                affected_sections=[section.id],
                related_suggestions=suggestion_data.get('related_sections', [])
            )
        except AIServiceError as e:
            print(f"[ERROR] Failed to generate suggestion for section {section.id}: {str(e)}")
            return None
    
    def _get_specialized_system_prompt(
        self, 
        section: DocumentSection, 
        change_context: dict[str, Any]
    ) -> str:
        """Get specialized system prompt based on section type and change context."""
        
        base_prompt = """You are an expert technical writer specializing in the OpenAI Agents SDK documentation.
        You understand the SDK's architecture with Agents, Handoffs, Guardrails, and Tools.
        
        Key concepts to maintain consistency:
        - Agents: LLMs with instructions and tools
        - Handoffs: Agent delegation mechanism  
        - Guardrails: Input validation system
        - Runner: Execution engine for agent workflows
        - Tools: Python functions that agents can call
        
        """
        
        # Add section-specific context
        if section.section_type == DocumentType.CODE:
            base_prompt += """
            This section contains code examples. When updating:
            - Maintain proper Python syntax and imports
            - Keep code examples simple and functional
            - Update import statements if APIs changed
            - Ensure code examples are consistent with current SDK version
            """
        
        # Add change-specific context
        change_type = change_context.get('change_type', '')
        if change_type == 'deprecation':
            base_prompt += """
            This is a deprecation change. When updating:
            - Clearly mark deprecated features
            - Provide migration path to new approach
            - Include timeline for deprecation if available
            - Update code examples to use new patterns
            """
        elif change_type == 'new_feature':
            base_prompt += """
            This is a new feature addition. When updating:
            - Add comprehensive documentation for new features
            - Include practical code examples
            - Explain how it integrates with existing concepts
            - Update related sections that might be affected
            """
        
        base_prompt += """
        Respond in JSON format:
        {
            "should_update": boolean,
            "title": "Brief title for the update",
            "description": "What's being changed and why", 
            "suggested_content": "Complete updated content for the section",
            "reasoning": "Detailed explanation of changes",
            "confidence": 0.8,
            "impact_level": "high|medium|low",
            "related_sections": ["list", "of", "section", "titles", "that", "might", "need", "updates"]
        }
        
        Only suggest updates when confident they're needed. Preserve markdown formatting and code blocks.
        """
        
        return base_prompt
    
    def _get_specialized_user_prompt(
        self, 
        query: str, 
        section: DocumentSection,
        change_context: dict[str, Any]
    ) -> str:
        """Generate specialized user prompt for the AI model."""
        
        prompt = f"""
        UPDATE REQUEST: {query}
        
        CHANGE CONTEXT:
        - Type: {change_context.get('change_type', 'unknown')}
        - Affected concepts: {', '.join(change_context.get('affected_concepts', []))}
        - Scope: {change_context.get('scope', 'unknown')}
        
        SECTION TO ANALYZE:
        Title: {section.title}
        Type: {section.section_type}
        File: {section.file_path}
        Lines: {section.line_start}-{section.line_end}
        
        Current Content:
        ```
        {section.content}
        ```
        
        Based on the update request and change context, should this section be updated?
        If yes, provide the complete updated content maintaining the same format and style.
        """
        
        return prompt
    
    async def _generate_section_suggestion_fast(
        self, 
        query: str, 
        section: DocumentSection,
        change_context: dict[str, Any]
    ) -> UpdateSuggestion | None:
        """Fast version of section suggestion generation with optimized prompts."""
        try:
            system_prompt = self._get_fast_system_prompt()
            user_prompt = self._get_fast_user_prompt(query, section, change_context)
            response = await self._call_openai_api(system_prompt, user_prompt)
            if not response:
                return None
            suggestion_data = self._parse_ai_response(response)
            if not suggestion_data.get('should_update', False):
                return None
            original_content = section.content
            suggested_content = suggestion_data.get('suggested_content', '')
            if not suggested_content or suggested_content == original_content:
                return None
            diff_hunks = self.diff_service.generate_diff_hunks(
                original_content, 
                suggested_content
            )
            suggestion_type = self._determine_suggestion_type(
                suggestion_data, change_context
            )
            return UpdateSuggestion(
                id=self._generate_suggestion_id(),
                document_id=section.file_path,
                section_id=section.id,
                title=suggestion_data.get('title', f"Update {section.title}"),
                description=suggestion_data.get('description', ''),
                diff_hunks=diff_hunks,
                original_content=original_content,
                suggested_content=suggested_content,
                suggestion_type=suggestion_type,
                confidence_score=suggestion_data.get('confidence', 0.8),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                reasoning=suggestion_data.get('reasoning', ''),
                affected_sections=[section.id],
                related_suggestions=suggestion_data.get('related_sections', [])
            )
        except Exception as e:
            print(f"[ERROR] Failed to generate fast suggestion for section {section.id}: {str(e)}")
            return None
    
    def _get_fast_system_prompt(self) -> str:
        """Optimized system prompt for faster processing."""
        return """You are a documentation update assistant for OpenAI Agents SDK. 
        
        Key concepts: Agents (LLMs with tools), Handoffs (delegation), Guardrails (validation), Tools (functions), Runner (execution).
        
        Respond in JSON:
        {
            "should_update": boolean,
            "title": "Brief title",
            "description": "What's changing", 
            "suggested_content": "Updated content",
            "reasoning": "Why change",
            "confidence": 0.8
        }
        
        Only suggest updates when confident. Keep responses concise but accurate."""
    
    def _get_fast_user_prompt(
        self, 
        query: str, 
        section: DocumentSection,
        change_context: dict[str, Any]
    ) -> str:
        """Fast user prompt with minimal context."""
        return f"""UPDATE: {query}
        
        SECTION: {section.title}
        TYPE: {change_context.get('change_type', 'update')}
        
        CONTENT:
        {section.content[:500]}{'...' if len(section.content) > 500 else ''}
        
        Should this be updated? If yes, provide the complete updated content."""
    
    def _determine_suggestion_type(
        self, 
        suggestion_data: dict[str, Any], 
        change_context: dict[str, Any]
    ) -> SuggestionType:
        """Determine the type of suggestion based on content analysis and context."""
        
        change_type = change_context.get('change_type', '')
        
        if change_type == 'deprecation':
            return SuggestionType.UPDATE
        elif change_type == 'new_feature':
            return SuggestionType.ADD
        else:
            return SuggestionType.UPDATE
    
    async def _call_openai_api(self, system_prompt: str, user_prompt: str) -> str | None:
        """Call OpenAI API with enhanced error handling and timeout. Returns the raw response or None on error."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Fast model for speed
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Lower temperature for faster, more focused responses
                max_tokens=1000,  # Reduced for faster responses
                timeout=15  # Reduced timeout for faster responses
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[ERROR] OpenAI API error: {str(e)}")
            # Re-raise the exception to be caught by the router for proper error handling
            raise AIServiceError(f"OpenAI API call failed: {str(e)}")
    
    def _parse_ai_response(self, response: str) -> dict[str, Any]:
        """Parse the AI response, extracting JSON and handling errors gracefully."""
        try:
            # Try direct JSON parsing first
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            
            # Look for JSON blocks wrapped in ```json or ```
            json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            json_match = re.search(json_pattern, response, re.DOTALL)
            
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Look for any JSON-like structure
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # Return default structure if all parsing fails
            return {
                "should_update": False,
                "title": "Parse Error",
                "description": "Could not parse AI response",
                "suggested_content": "",
                "reasoning": f"Failed to parse AI response: {response[:200]}...",
                "confidence": 0.0,
                "impact_level": "low",
                "related_sections": []
            }
    
    def _generate_suggestion_id(self) -> str:
        """Generate a unique suggestion ID using UUID4."""
        return str(uuid.uuid4())