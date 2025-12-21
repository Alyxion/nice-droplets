from nicegui import ui
from typing import List
from nice_droplets.helpers.mongo_logger import MongoLogger
from nice_droplets.utils.compat import html as compat_html

class LogView(ui.element):
    def __init__(self, valid_categories: List[str], logger: MongoLogger):
        super().__init__()
        self.logger: MongoLogger = logger
        self.rows = []
        self.last_seen_timestamp = None
        self.valid_categories = valid_categories
        self.category_filter = valid_categories
        self.user_filter = ["*"]
        self.server_filter = ["*"]
        self.valid_servers = ["*"]
        self.table_html: ui.html | None = None
        self.category_element: ui.select | None = None
        self.user_filter_element: ui.select | None = None
        self.server_element: ui.select | None = None
        self.limit = 50
        self.limit_element: ui.select | None = None

    def format_row(self, log):
        from datetime import datetime, timezone, timedelta
        import pytz
        color_map = {
            "error": "bg-red-1 text-red-8",
            "warning": "bg-orange-1 text-orange-8",
            "success": "bg-green-1 text-green-8",
            "info": "bg-blue-1 text-blue-8",
            "default": ""
        }
        log_type = (log.get("type") or "").lower()
        color = color_map.get(log_type, "")
        ts = log.get("timestamp")
        ts_dt = ts
        ts_str = ""
        import pytz
        now_utc = datetime.now(timezone.utc)
        # Try to parse ts as datetime
        try:
            ts_dt = ts_dt.replace(tzinfo=timezone.utc)
            # Calculate time difference in UTC
            # ensure diff is not negative
            if ts_dt > now_utc:
                diff = 0.0
            else:
                diff = now_utc - ts_dt
            seconds = int(diff.total_seconds())
            # Show time of day in Europe/Berlin
            time_of_day = ts_dt.strftime("%H:%M:%S")
            if seconds < 60:
                ts_str = f"{seconds} seconds ago ({time_of_day})"
            elif seconds < 3600:
                mins = seconds // 60
                secs = seconds % 60
                ts_str = f"{mins} min {secs} sec ago ({time_of_day})"
            elif seconds < 86400:
                hours = seconds // 3600
                mins = (seconds % 3600) // 60
                ts_str = f"{hours} hr {mins} min ago ({time_of_day})"
            else:
                ts_str = ts_local.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            ts_str = str(ts_dt)
        return {
            "timestamp": ts_str,
            "timestamp_raw": ts_dt,  # always a datetime or None
            "message": log.get("message", ""),
            "type": log.get("type", ""),
            "category": log.get("category", ""),
            "user_mail": log.get("user_mail", ""),
            "server_name": log.get("server_name", ""),
            "_row_class": color
        }

    async def filter_changed(self, e):
        self.category_filter = self.category_element.value
        self.user_filter = self.user_filter_element.value
        self.server_filter = self.server_element.value
        self.limit = int(self.limit_element.value)
        await self.poll_new_logs()

    async def render_html_table(self, rows):
        header = """
        <table style='width:100%;border-collapse:collapse;'>
            <thead>
                <tr style='background:#eee;'>
                    <th style='padding:4px;border:1px solid #ccc;'>Timestamp</th>
                    <th style='padding:4px;border:1px solid #ccc;'>Message</th>
                    <th style='padding:4px;border:1px solid #ccc;'>Type</th>
                    <th style='padding:4px;border:1px solid #ccc;'>Category</th>
                    <th style='padding:4px;border:1px solid #ccc;'>User Mail</th>
                    <th style='padding:4px;border:1px solid #ccc;'>Server</th>
                </tr>
            </thead>
            <tbody>
        """
        color_map = {
            "error": "background-color:#ffe5e5;color:#c00;",
            "warning": "background-color:#fff4e5;color:#e67e22;",
            "success": "background-color:#e7ffe5;color:#27ae60;",
            "info": "background-color:#e5f0ff;color:#2980b9;",
            "default": ""
        }
        body = ""
        for row in rows:
            style = color_map.get((row.get("type") or "").lower(), "")
            body += f"<tr style='{style}'>"
            # Format timestamp to human-readable string (YYYY-MM-DD HH:MM:SS)
            ts = row['timestamp']
            if hasattr(ts, 'strftime'):
                ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(ts, str):
                try:
                    from datetime import datetime
                    ts_str = datetime.fromisoformat(ts.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    ts_str = ts
            else:
                ts_str = str(ts)
            body += f"<td style='padding:4px;border:1px solid #ccc;'>{ts_str}</td>"
            body += f"<td style='padding:4px;border:1px solid #ccc;'>{row['message']}</td>"
            body += f"<td style='padding:4px;border:1px solid #ccc;'>{row['type']}</td>"
            body += f"<td style='padding:4px;border:1px solid #ccc;'>{row['category']}</td>"
            body += f"<td style='padding:4px;border:1px solid #ccc;'>{row['user_mail']}</td>"
            body += f"<td style='padding:4px;border:1px solid #ccc;'>{row.get('server_name','')}</td>"
            body += "</tr>"
        body += "</tbody></table>"
        return header + body

    async def poll_new_logs(self):
        # Build category filter
        add_filter = {"category": {"$in": self.category_filter}}
        # Build user_mail filter if needed
        user_filters = self.user_filter
        if user_filters and not (len(user_filters) == 1 and user_filters[0] == "*"):
            or_clauses = []
            import re
            for f in user_filters:
                if '*' in f:
                    # Convert shell-style wildcards to MongoDB regex
                    pattern = re.escape(f).replace('\\*', '.*')
                    # Always match anywhere in the string
                    if not pattern.startswith('.*'):
                        pattern = '.*' + pattern
                    if not pattern.endswith('.*'):
                        pattern = pattern + '.*'
                    or_clauses.append({"user_mail": {"$regex": pattern, "$options": "i"}})
                else:
                    # Exact match, but still case-insensitive
                    or_clauses.append({"user_mail": {"$regex": f"^{re.escape(f)}$", "$options": "i"}})
            add_filter = {**add_filter, "$or": or_clauses}
        # Build server_name filter if needed
        server_filters = self.server_filter
        if server_filters and not (len(server_filters) == 1 and server_filters[0] == "*"):
            server_or_clauses = []
            import re
            for s in server_filters:
                if '*' in s:
                    # Escape regex special chars except '*', then replace '*' with '.*'
                    pattern = re.escape(s).replace('\\*', '.*')
                    server_or_clauses.append({"server_name": {"$regex": pattern}})
                else:
                    server_or_clauses.append({"server_name": s})
            if "$or" in add_filter:
                # Combine with existing $or (user_mail)
                add_filter["$and"] = [{"$or": add_filter["$or"]}, {"$or": server_or_clauses}]
                del add_filter["$or"]
            else:
                add_filter["$or"] = server_or_clauses
        logs = await self.logger.fetch_recent_messages_async(
            limit=self.limit, fields=["timestamp", "message", "type", "category", "user_mail", "server_name"],
            add_filter=add_filter
        )
        formatted = [self.format_row(log) for log in logs]
        formatted.sort(key=lambda r: r["timestamp_raw"], reverse=True)
        self.rows.clear()
        self.rows.extend(formatted[:100])
        # Auto-extend valid servers and user mails
        servers = set(self.valid_servers+['*'])
        emails = set(self.user_filter+['*'])
        for log in logs:
            if log.get("server_name"):
                servers.add(log["server_name"])
            if log.get("user_mail"):
                emails.add(log["user_mail"])
        self.valid_servers = sorted(list(set(servers).union(set(self.server_element.options))))
        self.valid_emails = sorted(list(set(emails).union(set(self.user_filter_element.options))))
        if self.server_element:
            if self.server_element.options != self.valid_servers:
                self.server_element.options = self.valid_servers
                self.server_element.update()
        if self.user_filter_element:
            if self.user_filter_element.options != sorted(emails):
                self.user_filter_element.options = sorted(emails)
                self.user_filter_element.update()
        self.table_html.content = await self.render_html_table(self.rows)
        
    async def build(self):
        columns = [
            {"name": "timestamp", "label": "Timestamp", "field": "timestamp", "sortable": True, "align": "left"},
            {"name": "message", "label": "Message", "field": "message", "sortable": False, "align": "left"},
            {"name": "type", "label": "Type", "field": "type", "sortable": True, "align": "left"},
            {"name": "category", "label": "Category", "field": "category", "sortable": True, "align": "left"},
            {"name": "user_mail", "label": "User Mail", "field": "user_mail", "sortable": True, "align": "left"},
            {"name": "server_name", "label": "Server", "field": "server_name", "sortable": True, "align": "left"},
        ]
        # Dropdown for number of elements to fetch
        limit_options = [20, 50, 100, 200]
        limit_select = ui.select(limit_options, value=self.limit, label='Show N logs').classes('w-64')
        limit_select.on_value_change(self.filter_changed)
        self.limit_element = limit_select

        cat_select = ui.select(self.valid_categories, multiple=True, value=self.category_filter, label='Categories').classes('w-256').props('use-chips')
        cat_select.on_value_change(self.filter_changed)
        e_mail_select = ui.select(self.user_filter, multiple=True, value=self.user_filter, label='User Mail', new_value_mode='add-unique').classes('w-256').props('use-chips')
        e_mail_select.on_value_change(self.filter_changed)
        # Server filter
        server_select = ui.select(["*"] + self.valid_servers, multiple=True, value=self.server_filter, label='Server', new_value_mode='add-unique').classes('w-256').props('use-chips')
        server_select.on_value_change(self.filter_changed)
        self.category_element = cat_select
        self.user_filter_element = e_mail_select
        self.server_element = server_select
        with ui.row():
            limit_select
            cat_select
            e_mail_select
            server_select
        self.table_html = compat_html("<div>Loading logs...</div>")

        await self.poll_new_logs()
        ui.timer(5.0, self.poll_new_logs, active=True)