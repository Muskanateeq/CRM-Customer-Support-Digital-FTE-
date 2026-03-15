"""
Smart Parser Utilities for TaskNest Chatbot

Handles intelligent parsing of:
- Dates (multiple formats, natural language, Urdu)
- Priorities (English + Urdu)
- Tags (auto-resolution)
- Language detection
"""

from datetime import datetime, timedelta
from typing import Optional, List
import re
from dateutil import parser as date_parser


class SmartParser:
    """Intelligent parsing for natural language inputs"""

    # Urdu/Hindi date keywords
    URDU_DATE_KEYWORDS = {
        "kal": 1,  # tomorrow
        "parso": 2,  # day after tomorrow
        "aaj": 0,  # today
    }

    # Priority mappings
    PRIORITY_MAP = {
        # English
        "high": "high",
        "urgent": "high",
        "important": "high",
        "critical": "high",
        "asap": "high",

        "medium": "medium",
        "normal": "medium",
        "moderate": "medium",

        "low": "low",
        "minor": "low",
        "later": "low",

        # Urdu/Hindi
        "zaruri": "high",
        "zaroori": "high",
        "bohot": "high",
        "jaldi": "high",

        "thik": "medium",
        "theek": "medium",
        "normal": "medium",

        "kam": "low",
        "baad": "low",
    }

    @staticmethod
    def parse_date(date_str: str) -> Optional[str]:
        """
        Parse date from multiple formats and return YYYY-MM-DD.

        Supports:
        - ISO format: "2026-02-26"
        - DD-MM-YYYY: "26-02-2026"
        - DD/MM/YYYY: "26/02/2026"
        - Natural: "tomorrow", "next week"
        - Urdu: "kal", "parso"

        Args:
            date_str: Date string in any format

        Returns:
            Date in YYYY-MM-DD format or None if invalid
        """
        if not date_str:
            return None

        date_str = date_str.strip().lower()

        # Check Urdu keywords
        for urdu_word, days_offset in SmartParser.URDU_DATE_KEYWORDS.items():
            if urdu_word in date_str:
                target_date = datetime.now() + timedelta(days=days_offset)
                return target_date.strftime("%Y-%m-%d")

        # Check English natural language
        if "tomorrow" in date_str or "tmrw" in date_str:
            target_date = datetime.now() + timedelta(days=1)
            return target_date.strftime("%Y-%m-%d")

        if "today" in date_str:
            return datetime.now().strftime("%Y-%m-%d")

        if "next week" in date_str:
            target_date = datetime.now() + timedelta(days=7)
            return target_date.strftime("%Y-%m-%d")

        # Handle "after X days/weeks/months" OR "in X days/weeks/months"
        after_pattern = r"(?:after|in)\s+(\d+)\s+(day|days|week|weeks|month|months)"
        match = re.search(after_pattern, date_str)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)

            if "day" in unit:
                target_date = datetime.now() + timedelta(days=amount)
            elif "week" in unit:
                target_date = datetime.now() + timedelta(weeks=amount)
            elif "month" in unit:
                # Approximate: 30 days per month
                target_date = datetime.now() + timedelta(days=amount * 30)

            return target_date.strftime("%Y-%m-%d")

        # Try DD-MM-YYYY or DD/MM/YYYY format
        dd_mm_yyyy_pattern = r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})"
        match = re.match(dd_mm_yyyy_pattern, date_str)
        if match:
            day, month, year = match.groups()
            try:
                parsed_date = datetime(int(year), int(month), int(day))
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                pass

        # Try standard date parsing (handles many formats)
        try:
            parsed_date = date_parser.parse(date_str, dayfirst=True)
            return parsed_date.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    @staticmethod
    def parse_priority(priority_str: str) -> str:
        """
        Parse priority from English or Urdu.

        Args:
            priority_str: Priority string (e.g., "high", "zaruri", "urgent")

        Returns:
            Normalized priority: "high", "medium", or "low"
        """
        if not priority_str:
            return "medium"

        priority_str = priority_str.strip().lower()

        # Direct lookup
        if priority_str in SmartParser.PRIORITY_MAP:
            return SmartParser.PRIORITY_MAP[priority_str]

        # Partial match
        for key, value in SmartParser.PRIORITY_MAP.items():
            if key in priority_str or priority_str in key:
                return value

        # Default
        return "medium"

    @staticmethod
    async def resolve_tags(
        user_id: str,
        tag_names: List[str],
        session
    ) -> List[int]:
        """
        Resolve tag names to tag IDs, creating tags if they don't exist.

        Args:
            user_id: User ID
            tag_names: List of tag names
            session: Database session

        Returns:
            List of tag IDs
        """
        from src.services.tag_service import TagService
        from src.models.tag import TagCreate

        tag_ids = []

        for tag_name in tag_names:
            tag_name_clean = tag_name.strip()
            if not tag_name_clean:
                continue

            # Get all user tags
            all_tags = await TagService.get_user_tags(
                user_id=user_id,
                session=session
            )

            # Find matching tag (case-insensitive)
            matching_tag = None
            for tag in all_tags:
                if tag.name.lower() == tag_name_clean.lower():
                    matching_tag = tag
                    break

            if matching_tag:
                tag_ids.append(matching_tag.id)
            else:
                # Create new tag
                new_tag = await TagService.create_tag(
                    user_id=user_id,
                    tag_data=TagCreate(name=tag_name_clean),
                    session=session
                )
                tag_ids.append(new_tag.id)

        return tag_ids

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect if text contains Urdu/Hindi words.

        Args:
            text: Input text

        Returns:
            "urdu" if Urdu/Hindi detected, "english" otherwise
        """
        urdu_keywords = [
            "kal", "parso", "aaj", "zaruri", "zaroori", "karo", "kardo",
            "banao", "dikhao", "batao", "hai", "tha", "ho", "ka", "ki",
            "ko", "mein", "se", "par", "tak"
        ]

        text_lower = text.lower()
        for keyword in urdu_keywords:
            if keyword in text_lower:
                return "urdu"

        return "english"

    @staticmethod
    def parse_time(time_str: str) -> Optional[str]:
        """
        Parse time from various formats to HH:MM (24-hour).

        Supports:
        - "2pm", "14:00", "2:30 PM"
        - "do baje" (Urdu for 2 o'clock)

        Args:
            time_str: Time string

        Returns:
            Time in HH:MM format or None
        """
        if not time_str:
            return None

        time_str = time_str.strip().lower()

        # Handle "X baje" (Urdu)
        baje_pattern = r"(\d{1,2})\s*baje"
        match = re.search(baje_pattern, time_str)
        if match:
            hour = int(match.group(1))
            return f"{hour:02d}:00"

        # Handle "Xpm" or "Xam"
        am_pm_pattern = r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)"
        match = re.search(am_pm_pattern, time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            am_pm = match.group(3)

            if am_pm == "pm" and hour != 12:
                hour += 12
            elif am_pm == "am" and hour == 12:
                hour = 0

            return f"{hour:02d}:{minute:02d}"

        # Handle 24-hour format
        time_pattern = r"(\d{1,2}):(\d{2})"
        match = re.search(time_pattern, time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"

        return None
