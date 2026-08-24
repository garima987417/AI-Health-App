import json
import os
from datetime import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

VERSION = "V19 Android"
DATA_FILE = "ai_health_v19_data.json"


# ---------------- DATA ----------------

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "username": "",
        "password": "",
        "age": 0,
        "results": [],
        "journal": [],
        "goals": [],
        "completed_goals": [],
        "login_count": 0
    }


data = load_data()


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def now():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


def today():
    return datetime.now().strftime("%d-%m-%Y")


# ---------------- UI HELPERS ----------------

def title(text):
    return Label(
        text=text,
        font_size="22sp",
        bold=True,
        size_hint_y=None,
        height=55
    )


def info(text, size=16):
    return Label(
        text=text,
        font_size=f"{size}sp",
        halign="left",
        valign="top",
        text_size=(None, None),
        size_hint_y=None,
        height=50
    )


def button(text, callback, height=52):
    b = Button(text=text, font_size="16sp", size_hint_y=None, height=height)
    b.bind(on_press=callback)
    return b


def scroll_layout():
    scroll = ScrollView()
    box = BoxLayout(
        orientation="vertical",
        spacing=8,
        padding=12,
        size_hint_y=None
    )
    box.bind(minimum_height=box.setter("height"))
    scroll.add_widget(box)
    return scroll, box


# ---------------- LOGIN ----------------

class LoginScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()

        scroll, box = scroll_layout()
        box.add_widget(title("🩺 AI HEALTH APP\nVERSION 19"))

        box.add_widget(info("Login / Account", 19))

        self.username = TextInput(
            hint_text="Username",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        self.password = TextInput(
            hint_text="Password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=50
        )
        self.age = TextInput(
            hint_text="Age (new account only)",
            input_filter="int",
            multiline=False,
            size_hint_y=None,
            height=50
        )

        box.add_widget(self.username)
        box.add_widget(self.password)
        box.add_widget(self.age)

        box.add_widget(button("🔐 Login", self.login))
        box.add_widget(button("👤 Create Account", self.create_account))

        self.message = Label(
            text="",
            font_size="15sp",
            size_hint_y=None,
            height=60
        )
        box.add_widget(self.message)

        self.add_widget(scroll)

    def login(self, *_):
        u = self.username.text.strip()
        p = self.password.text

        if u == data["username"] and p == data["password"]:
            data["login_count"] += 1
            save_data()
            self.message.text = "✅ Login successful!"
            self.manager.current = "home"
        else:
            self.message.text = "❌ Username ya password galat hai."

    def create_account(self, *_):
        u = self.username.text.strip()
        p = self.password.text
        a = self.age.text.strip()

        if not u:
            self.message.text = "⚠️ Username likhiye."
            return
        if len(p) < 4:
            self.message.text = "⚠️ Password kam se kam 4 characters ka ho."
            return
        try:
            age = int(a)
            if age <= 0:
                raise ValueError
        except ValueError:
            self.message.text = "⚠️ Valid age likhiye."
            return

        data["username"] = u
        data["password"] = p
        data["age"] = age
        save_data()
        self.message.text = "✅ Account create ho gaya. Ab Login dabaiye."


# ---------------- HOME ----------------

class HomeScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()

        scroll, box = scroll_layout()
        box.add_widget(title("🏠 AI HEALTH APP"))

        latest = ""
        if data["results"]:
            r = data["results"][-1]
            latest = f"\nLatest Score: {r['score']}/10\n{r['level']}"

        box.add_widget(info(
            f"👤 {data['username']}   🎂 Age: {data['age']}\n"
            f"🩺 Checks: {len(data['results'])}   "
            f"📔 Journals: {len(data['journal'])}\n"
            f"🎯 Goals: {len(data['goals'])}   "
            f"🏆 Completed: {len(data['completed_goals'])}"
            + latest
        ))

        box.add_widget(button("🩺 Mental Health Check", lambda *_: self.go("check")))
        box.add_widget(button("🤖 AI Chat Assistant", lambda *_: self.go("chat")))
        box.add_widget(button("📋 Previous Results", lambda *_: self.go("results")))
        box.add_widget(button("📈 Mood Progress", lambda *_: self.go("progress")))
        box.add_widget(button("📔 Daily Mood Journal", lambda *_: self.go("journal")))
        box.add_widget(button("📖 View Mood Journal", lambda *_: self.go("view_journal")))
        box.add_widget(button("🌱 Wellness Tip", lambda *_: self.go("tip")))
        box.add_widget(button("📅 Mood Calendar", lambda *_: self.go("calendar")))
        box.add_widget(button("🎯 Set Daily Goal", lambda *_: self.go("goal")))
        box.add_widget(button("📋 View Goals", lambda *_: self.go("goals")))
        box.add_widget(button("🏆 Complete Goal", lambda *_: self.go("complete")))
        box.add_widget(button("👤 Profile", lambda *_: self.go("profile")))
        box.add_widget(button("📊 Health Summary", lambda *_: self.go("summary")))
        box.add_widget(button("🔐 Change Password", lambda *_: self.go("password")))
        box.add_widget(button("🚪 Logout", self.logout))

        self.add_widget(scroll)

    def go(self, screen):
        self.manager.current = screen

    def logout(self, *_):
        self.manager.current = "login"


# ---------------- HEALTH CHECK ----------------

class CheckScreen(Screen):
    questions = [
        "Kya aap stressed feel karte hain?",
        "Kya aapko tension ya worry hoti hai?",
        "Kya aapko relax karna mushkil lagta hai?",
        "Kya school/work ka pressure feel hota hai?",
        "Kya aapka mood aksar low ya worried rehta hai?"
    ]

    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        scroll, box = scroll_layout()

        box.add_widget(title("🩺 Mental Health Check"))
        box.add_widget(info("Har question ka answer 0, 1 ya 2 dein:\n0 = Kabhi Nahi | 1 = Kabhi-Kabhi | 2 = Aksar"))

        self.inputs = []
        for q in self.questions:
            box.add_widget(info(q, 15))
            t = TextInput(
                hint_text="0 - 2",
                input_filter="int",
                multiline=False,
                size_hint_y=None,
                height=48
            )
            self.inputs.append(t)
            box.add_widget(t)

        box.add_widget(button("📊 Submit Check", self.submit))
        self.result = Label(text="", font_size="16sp", size_hint_y=None, height=100)
        box.add_widget(self.result)
        box.add_widget(button("⬅️ Back", lambda *_: self.back()))

        self.add_widget(scroll)

    def submit(self, *_):
        score = 0

        for t in self.inputs:
            try:
                n = int(t.text)
            except ValueError:
                self.result.text = "⚠️ Har answer 0, 1 ya 2 hona chahiye."
                return

            if n not in (0, 1, 2):
                self.result.text = "⚠️ Sirf 0, 1 ya 2 likhiye."
                return
            score += n

        if score <= 3:
            level = "Low Stress 🙂"
        elif score <= 6:
            level = "Moderate Stress 😐"
        else:
            level = "High Stress 😟"

        data["results"].append({
            "date": now(),
            "score": score,
            "level": level
        })
        save_data()

        self.result.text = (
            f"Total Score: {score}/10\n"
            f"Level: {level}\n\n"
            "⚠️ Ye preliminary screening hai, medical diagnosis nahi."
        )

    def back(self):
        self.manager.current = "home"


# ---------------- CHAT ----------------

class ChatScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        scroll, box = scroll_layout()

        box.add_widget(title("🤖 AI Chat Assistant"))
        box.add_widget(info("Apni problem likhiye. Ye simple offline assistant hai."))

        self.output = Label(
            text="🤖 AI: Main sun raha hoon.",
            font_size="15sp",
            halign="left",
            valign="top",
            size_hint_y=None,
            height=100
        )
        box.add_widget(self.output)

        self.input = TextInput(
            hint_text="Apni problem likhiye...",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        box.add_widget(self.input)
        box.add_widget(button("💬 Send", self.send))
        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))

        self.add_widget(scroll)

    def send(self, *_):
        msg = self.input.text.lower().strip()

        if not msg:
            return

        if any(x in msg for x in ["stress", "tension", "pressure"]):
            reply = "Thoda break lena aur kisi trusted person se baat karna helpful ho sakta hai."
        elif any(x in msg for x in ["sad", "udaas", "dukhi", "low"]):
            reply = "Aapki feelings important hain. Kisi trusted person se share karna helpful ho sakta hai."
        elif any(x in msg for x in ["study", "padhai", "school"]):
            reply = "Padhai ko small tasks mein divide karke short breaks lena helpful ho sakta hai."
        elif any(x in msg for x in ["sleep", "neend"]):
            reply = "Regular sleep routine aur relaxing bedtime activity helpful ho sakti hai."
        elif any(x in msg for x in ["happy", "khush"]):
            reply = "😊 Achhi baat hai! Apni positive activities continue rakhiye."
        else:
            reply = "Main sun raha hoon. Aap apni feelings kisi trusted person ke saath share kar sakte hain."

        self.output.text = "🤖 AI: " + reply
        self.input.text = ""


# ---------------- RESULTS / PROGRESS ----------------

class ResultsScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        scroll, box = scroll_layout()
        box.add_widget(title("📋 Previous Results"))

        if not data["results"]:
            box.add_widget(info("Abhi koi result nahi hai."))
        else:
            for i, r in enumerate(data["results"], 1):
                box.add_widget(info(
                    f"{i}. {r['date']}\nScore: {r['score']}/10 | {r['level']}",
                    15
                ))

        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))
        self.add_widget(scroll)


class ProgressScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        scroll, box = scroll_layout()
        box.add_widget(title("📈 Mood Progress"))

        if not data["results"]:
            box.add_widget(info("Pehle health check complete kijiye."))
        else:
            scores = [r["score"] for r in data["results"]]
            avg = sum(scores) / len(scores)
            box.add_widget(info(
                f"Total Checks: {len(scores)}\n"
                + "\n".join(f"{i}. {s}/10" for i, s in enumerate(scores, 1))
                + f"\n\n📊 Average Score: {avg:.2f}/10"
            ))

        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))
        self.add_widget(scroll)


# ---------------- JOURNAL ----------------

class JournalScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        scroll, box = scroll_layout()
        box.add_widget(title("📔 Daily Mood Journal"))

        self.mood = TextInput(
            hint_text="Aaj ka mood...",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        self.note = TextInput(
            hint_text="Aaj ke baare mein kuch likhiye...",
            multiline=True,
            size_hint_y=None,
            height=100
        )

        box.add_widget(self.mood)
        box.add_widget(self.note)
        box.add_widget(button("💾 Save Journal", self.save))
        self.status = Label(text="", size_hint_y=None, height=50)
        box.add_widget(self.status)
        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))
        self.add_widget(scroll)

    def save(self, *_):
        mood = self.mood.text.strip()
        if not mood:
            self.status.text = "⚠️ Mood likhna zaroori hai."
            return

        data["journal"].append({
            "date": now(),
            "mood": mood,
            "note": self.note.text.strip()
        })
        save_data()
        self.status.text = "✅ Journal saved!"
        self.mood.text = ""
        self.note.text = ""


class ViewJournalScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        scroll, box = scroll_layout()
        box.add_widget(title("📖 My Mood Journal"))

        if not data["journal"]:
            box.add_widget(info("Abhi journal empty hai."))
        else:
            for i, e in enumerate(data["journal"], 1):
                box.add_widget(info(
                    f"{i}. {e['date']}\n😊 Mood: {e['mood']}\n📝 {e['note']}",
                    15
                ))

        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))
        self.add_widget(scroll)


class CalendarScreen(ViewJournalScreen):
    def build(self):
        self.clear_widgets()
        scroll, box = scroll_layout()
        box.add_widget(title("📅 Mood Calendar"))

        for e in data["journal"]:
            box.add_widget(info(f"📅 {e['date']} | Mood: {e['mood']}", 15))

        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))
        self.add_widget(scroll)


# ---------------- TIPS / GOALS ----------------

class TipScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        box = BoxLayout(orientation="vertical", padding=20, spacing=12)
        box.add_widget(title("🌱 Daily Wellness Tip"))
        tips = [
            "💧 Paani peena yaad rakhiye.",
            "🚶 Thodi physical activity kijiye.",
            "📵 Screen se short break lijiye.",
            "😴 Regular sleep routine rakhiye.",
            "🧘 Kuch minutes relax kijiye.",
            "💬 Kisi trusted person se baat kijiye."
        ]
        day = datetime.now().timetuple().tm_yday
        box.add_widget(info(tips[day % len(tips)], 18))
        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))
        self.add_widget(box)


class GoalScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        box = BoxLayout(orientation="vertical", padding=20, spacing=12)
        box.add_widget(title("🎯 Set Daily Wellness Goal"))

        self.goal = TextInput(
            hint_text="Aaj ka goal...",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        box.add_widget(self.goal)
        box.add_widget(button("💾 Save Goal", self.save))
        self.status = Label(text="", size_hint_y=None, height=50)
        box.add_widget(self.status)
        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))
        self.add_widget(box)

    def save(self, *_):
        g = self.goal.text.strip()
        if not g:
            self.status.text = "⚠️ Goal empty nahi ho sakta."
            return
        data["goals"].append({"date": today(), "goal": g})
        save_data()
        self.status.text = "✅ Goal saved!"
        self.goal.text = ""


class GoalsScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        scroll, box = scroll_layout()
        box.add_widget(title("📋 My Goals"))

        for i, g in enumerate(data["goals"], 1):
            box.add_widget(info(f"{i}. {g['date']} - {g['goal']}", 15))

        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))
        self.add_widget(scroll)


class CompleteGoalScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        box = BoxLayout(orientation="vertical", padding=20, spacing=12)
        box.add_widget(title("🏆 Complete Goal"))

        if data["goals"]:
            latest = data["goals"][-1]
            box.add_widget(info("Today's Goal:\n" + latest["goal"], 18))
            box.add_widget(button("✅ Yes, complete", self.complete))
            box.add_widget(button("❌ Not yet", lambda *_: self.not_yet))
        else:
            box.add_widget(info("Pehle goal set kijiye."))

        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))
        self.status = Label(text="", size_hint_y=None, height=50)
        box.add_widget(self.status)
        self.add_widget(box)

    def complete(self, *_):
        data["completed_goals"].append(now())
        save_data()
        self.status.text = "🎉 Great! Goal completed!"

    def not_yet(self, *_):
        self.status.text = "💪 Koi baat nahi. Kal phir try kijiye."


# ---------------- PROFILE / SUMMARY / PASSWORD ----------------

class ProfileScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        box = BoxLayout(orientation="vertical", padding=20, spacing=10)
        box.add_widget(title("👤 My Profile"))
        box.add_widget(info(
            f"Username: {data['username']}\n"
            f"Age: {data['age']}\n"
            f"Version: {VERSION}\n"
            f"Health Checks: {len(data['results'])}\n"
            f"Journal Entries: {len(data['journal'])}\n"
            f"Goals: {len(data['goals'])}\n"
            f"Completed Goals: {len(data['completed_goals'])}\n"
            f"Login Count: {data['login_count']}"
        ))
        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))
        self.add_widget(box)


class SummaryScreen(ProfileScreen):
    def build(self):
        self.clear_widgets()
        box = BoxLayout(orientation="vertical", padding=20, spacing=10)
        box.add_widget(title("📊 Complete Health Summary"))

        text = (
            f"👤 Username: {data['username']}\n"
            f"🎂 Age: {data['age']}\n\n"
            f"🩺 Health Checks: {len(data['results'])}\n"
            f"📔 Journal Entries: {len(data['journal'])}\n"
            f"🎯 Goals: {len(data['goals'])}\n"
            f"🏆 Completed Goals: {len(data['completed_goals'])}\n"
        )

        if data["results"]:
            scores = [r["score"] for r in data["results"]]
            text += (
                f"\n📈 Average: {sum(scores)/len(scores):.2f}/10\n"
                f"📊 Latest: {scores[-1]}/10\n"
                f"⭐ Highest: {max(scores)}/10\n"
                f"🌱 Lowest: {min(scores)}/10"
            )

        if data["journal"]:
            text += f"\n\n😊 Latest Mood: {data['journal'][-1]['mood']}"

        box.add_widget(info(text, 16))
        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))
        self.add_widget(box)


class PasswordScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        box = BoxLayout(orientation="vertical", padding=20, spacing=10)
        box.add_widget(title("🔐 Change Password"))

        self.old = TextInput(hint_text="Current password", password=True, multiline=False, size_hint_y=None, height=50)
        self.new = TextInput(hint_text="New password", password=True, multiline=False, size_hint_y=None, height=50)
        self.confirm = TextInput(hint_text="Confirm new password", password=True, multiline=False, size_hint_y=None, height=50)

        box.add_widget(self.old)
        box.add_widget(self.new)
        box.add_widget(self.confirm)
        box.add_widget(button("🔐 Change Password", self.change))
        self.status = Label(text="", size_hint_y=None, height=50)
        box.add_widget(self.status)
        box.add_widget(button("⬅️ Back", lambda *_: setattr(self.manager, "current", "home")))
        self.add_widget(box)

    def change(self, *_):
        if self.old.text != data["password"]:
            self.status.text = "❌ Current password galat hai."
            return
        if len(self.new.text) < 4:
            self.status.text = "⚠️ Password kam se kam 4 characters ka ho."
            return
        if self.new.text != self.confirm.text:
            self.status.text = "❌ Password match nahi karte."
            return

        data["password"] = self.new.text
        save_data()
        self.status.text = "✅ Password changed!"


# ---------------- APP ----------------

class AIHealthApp(App):
    def build(self):
        Window.softinput_mode = "below_target"

        sm = ScreenManager()
        screens = [
            ("login", LoginScreen()),
            ("home", HomeScreen()),
            ("check", CheckScreen()),
            ("chat", ChatScreen()),
            ("results", ResultsScreen()),
            ("progress", ProgressScreen()),
            ("journal", JournalScreen()),
            ("view_journal", ViewJournalScreen()),
            ("tip", TipScreen()),
            ("calendar", CalendarScreen()),
            ("goal", GoalScreen()),
            ("goals", GoalsScreen()),
            ("complete", CompleteGoalScreen()),
            ("profile", ProfileScreen()),
            ("summary", SummaryScreen()),
            ("password", PasswordScreen()),
        ]

        for name, screen in screens:
            sm.add_widget(screen)
        sm.current = "login"
        return sm


if __name__ == "__main__":
    AIHealthApp().run()
