import re

class LogParser:
    def __init__(self):
        # Optimized to catch 'test_calculator.py:3' as seen in your logs
        self.pattern = r'([a-zA-Z0-9_\-/]+\.py):(\d+)'

    def parse_error(self, logs: str):
        # Look for the last mention of a .py file with a line number
        matches = re.findall(self.pattern, logs)
        if matches:
            for file, line in reversed(matches):
                # Filter out pytest/system files
                if "test" in file or "calculator" in file:
                    return file, line, self._get_last_line(logs)
        
        return None, None, "No specific failure line found in logs."

    def _get_last_line(self, logs):
        lines = [l.strip() for l in logs.split('\n') if l.strip()]
        return lines[-1] if lines else "Unknown Error"