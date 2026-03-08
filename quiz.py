import random
import sys

import pygame


STARTING_QUESTIONS = [
    {"q": "What comes after 1?", "a": "2", "h": "hint here"},
    {"q": 'What part of speech is "me"?', "a": "pron.", "h": "hint here"},
    {"q": "What famous tower is in Paris?", "a": "Eiffel Tower", "h": "hint here"},
    {"q": "What fruit do you get from an orange tree?", "a": "Orange", "h": "hint here"},
]

WIDTH, HEIGHT = 900, 560
BG = (241, 245, 249)
CARD = (255, 255, 255)
TEXT = (17, 24, 39)
MUTED = (75, 85, 99)
PRIMARY = (15, 118, 110)
PRIMARY_HOVER = (17, 94, 89)
SECONDARY = (229, 231, 235)
SECONDARY_HOVER = (209, 213, 219)
INPUT_BG = (249, 250, 251)
INPUT_BORDER = (156, 163, 175)
INPUT_ACTIVE = (14, 116, 144)
ANSWER_BG = (236, 253, 245)
ANSWER_TEXT = (6, 95, 70)


class Button:
    def __init__(self, x, y, w, h, label, kind="secondary"):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.kind = kind
        self.visible = True
        self.enabled = True

    def set_rect(self, x, y, w, h):
        self.rect.update(int(x), int(y), int(w), int(h))

    def clicked(self, event):
        return (
            self.visible
            and self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, screen, font, mouse_pos):
        if not self.visible:
            return
        hovered = self.enabled and self.rect.collidepoint(mouse_pos)
        if self.kind == "primary":
            color = PRIMARY_HOVER if hovered else PRIMARY
            txt_color = (255, 255, 255)
        else:
            color = SECONDARY_HOVER if hovered else SECONDARY
            txt_color = TEXT
        if not self.enabled:
            color = (200, 205, 212)
            txt_color = (120, 126, 136)
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        txt = font.render(self.label, True, txt_color)
        screen.blit(txt, txt.get_rect(center=self.rect.center))


class TextInput:
    def __init__(self, label, text=""):
        self.label = label
        self.text = text
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.active = False
        self.visible = True
        self.enabled = True
        self.max_len = 140

    def set_rect(self, x, y, w, h):
        self.rect.update(int(x), int(y), int(w), int(h))

    def set_text(self, text):
        self.text = text

    def handle_event(self, event):
        if not (self.visible and self.enabled):
            return False
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                changed = True
            elif event.key == pygame.K_RETURN:
                pass
            else:
                if event.unicode and event.unicode.isprintable() and len(self.text) < self.max_len:
                    self.text += event.unicode
                    changed = True
        return changed

    def draw(self, screen, font_label, font_text):
        if not self.visible:
            return
        lbl = font_label.render(self.label, True, MUTED)
        screen.blit(lbl, (self.rect.x, self.rect.y - lbl.get_height() - 6))
        pygame.draw.rect(screen, INPUT_BG, self.rect, border_radius=8)
        border = INPUT_ACTIVE if self.active and self.enabled else INPUT_BORDER
        pygame.draw.rect(screen, border, self.rect, width=2, border_radius=8)
        txt = font_text.render(self.text if self.text else "", True, TEXT)
        screen.blit(txt, (self.rect.x + 10, self.rect.y + (self.rect.height - txt.get_height()) // 2))


class QuizApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Quiz Software")
        self.window_size = (WIDTH, HEIGHT)
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        self.mode = "play"
        self.is_fullscreen = False
        self.current_scale = None

        self.font_title = None
        self.font_text = None
        self.font_small = None
        self.font_btn = None

        self.questions = [q.copy() for q in STARTING_QUESTIONS]
        self.selected_idx = 0

        self.toggle_mode_btn = Button(16, 12, 120, 40, "Edit")
        self.fullscreen_btn = Button(760, 12, 130, 40, "Fullscreen")

        self.reveal_btn = Button(70, 390, 180, 52, "Reveal Answer", kind="primary")
        self.next_btn = Button(270, 390, 180, 52, "Next Question")
        self.hint_btn = Button(470, 390, 130, 52, "Hint")
        self.correct_btn = Button(70, 325, 180, 48, "Correct", kind="primary")
        self.incorrect_btn = Button(270, 325, 180, 48, "Incorrect")
        self.restart_btn = Button(470, 390, 130, 52, "Restart")
        self.close_btn = Button(470, 390, 130, 52, "Close")

        self.add_btn = Button(0, 0, 120, 46, "Add New")
        self.delete_btn = Button(0, 0, 140, 46, "Delete")

        self.q_input = TextInput("Question")
        self.a_input = TextInput("Answer")
        self.h_input = TextInput("Hint")
        self.editor_inputs = [self.q_input, self.a_input, self.h_input]

        self.start_play_mode()
        self.update_fonts()
        self.update_mode_controls()

    def update_fonts(self):
        w, h = self.screen.get_size()
        scale = int(min(w, h))
        if scale == self.current_scale:
            return
        self.current_scale = scale
        base = min(w, h)
        self.font_title = pygame.font.SysFont("arial", max(24, int(base * 0.055)), bold=True)
        self.font_text = pygame.font.SysFont("arial", max(18, int(base * 0.038)))
        self.font_small = pygame.font.SysFont("arial", max(15, int(base * 0.029)))
        self.font_btn = pygame.font.SysFont("arial", max(16, int(base * 0.031)))

    def start_play_mode(self):
        self.mode = "play"
        self.finished = False
        self.show_answer = False
        self.show_hint = False
        self.feedback_text = ""
        self.score = 0

        self.order = [q.copy() for q in self.questions]
        random.shuffle(self.order)
        self.index = 0
        self.marked = [None] * len(self.order)

        self.reveal_btn.visible = True
        self.reveal_btn.enabled = len(self.order) > 0
        self.next_btn.visible = True
        self.next_btn.enabled = False
        self.hint_btn.visible = True
        self.hint_btn.enabled = len(self.order) > 0
        self.correct_btn.visible = False
        self.incorrect_btn.visible = False
        self.restart_btn.visible = False
        self.close_btn.visible = False

        self.toggle_mode_btn.label = "Edit"
        self.update_mode_controls()

    def start_edit_mode(self):
        self.mode = "edit"
        self.toggle_mode_btn.label = "Play"
        if self.selected_idx >= len(self.questions):
            self.selected_idx = max(0, len(self.questions) - 1)
        self.load_selected_into_inputs()
        self.update_mode_controls()

    def update_mode_controls(self):
        play_visible = self.mode == "play"
        edit_visible = self.mode == "edit"
        for btn in [
            self.reveal_btn,
            self.next_btn,
            self.hint_btn,
            self.correct_btn,
            self.incorrect_btn,
            self.restart_btn,
            self.close_btn,
        ]:
            btn.visible = btn.visible and play_visible
        self.add_btn.visible = edit_visible
        self.delete_btn.visible = edit_visible
        for inp in self.editor_inputs:
            inp.visible = edit_visible
            inp.enabled = edit_visible and self.has_selected()

    def has_selected(self):
        return 0 <= self.selected_idx < len(self.questions)

    def load_selected_into_inputs(self):
        if self.has_selected():
            q = self.questions[self.selected_idx]
            self.q_input.set_text(q.get("q", ""))
            self.a_input.set_text(q.get("a", ""))
            self.h_input.set_text(q.get("h", ""))
            for inp in self.editor_inputs:
                inp.enabled = True
        else:
            self.q_input.set_text("")
            self.a_input.set_text("")
            self.h_input.set_text("")
            for inp in self.editor_inputs:
                inp.enabled = False
                inp.active = False

    def save_inputs_to_selected(self):
        if not self.has_selected():
            return
        self.questions[self.selected_idx]["q"] = self.q_input.text
        self.questions[self.selected_idx]["a"] = self.a_input.text
        self.questions[self.selected_idx]["h"] = self.h_input.text

    def add_question(self):
        self.save_inputs_to_selected()
        self.questions.append({"q": "New question", "a": "New answer", "h": "hint here"})
        self.selected_idx = len(self.questions) - 1
        self.load_selected_into_inputs()

    def delete_selected(self):
        if not self.has_selected():
            return
        self.questions.pop(self.selected_idx)
        if self.selected_idx >= len(self.questions):
            self.selected_idx = len(self.questions) - 1
        self.load_selected_into_inputs()

    def reveal_answer(self):
        if self.finished or not self.order:
            return
        self.show_answer = True
        self.reveal_btn.enabled = False
        self.next_btn.enabled = False
        self.correct_btn.visible = True
        self.incorrect_btn.visible = True
        self.correct_btn.enabled = True
        self.incorrect_btn.enabled = True
        self.feedback_text = ""

    def reveal_hint(self):
        if not self.finished and self.order:
            self.show_hint = True

    def mark_answer(self, is_correct):
        if self.finished or not self.show_answer or not self.order:
            return
        if self.marked[self.index] is not None:
            return
        self.marked[self.index] = is_correct
        if is_correct:
            self.score += 1
            self.feedback_text = "Marked: Correct"
        else:
            self.feedback_text = "Marked: Incorrect"
        self.correct_btn.enabled = False
        self.incorrect_btn.enabled = False
        self.next_btn.enabled = True

    def next_question(self):
        self.index += 1
        if self.index >= len(self.order):
            self.finished = True
            self.reveal_btn.visible = False
            self.next_btn.visible = False
            self.hint_btn.visible = False
            self.correct_btn.visible = False
            self.incorrect_btn.visible = False
            self.restart_btn.visible = True
            self.close_btn.visible = True
        else:
            self.show_answer = False
            self.show_hint = False
            self.feedback_text = ""
            self.reveal_btn.enabled = True
            self.next_btn.enabled = False
            self.correct_btn.visible = False
            self.incorrect_btn.visible = False

    def toggle_mode(self):
        if self.mode == "play":
            self.start_edit_mode()
        else:
            self.save_inputs_to_selected()
            self.start_play_mode()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.window_size = self.screen.get_size()
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.fullscreen_btn.label = "Windowed"
        else:
            self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
            self.fullscreen_btn.label = "Fullscreen"
        self.update_fonts()

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        line = ""
        for word in words:
            test = word if not line else f"{line} {word}"
            if font.size(test)[0] <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    def update_layout(self):
        self.update_fonts()
        w, h = self.screen.get_size()
        self.card = pygame.Rect(int(w * 0.04), int(h * 0.09), int(w * 0.92), int(h * 0.86))

        top_h = max(36, int(h * 0.06))
        top_w = max(110, int(w * 0.12))
        self.toggle_mode_btn.set_rect(16, 12, top_w, top_h)
        self.fullscreen_btn.set_rect(w - top_w - 16, 12, top_w, top_h)

        pad = max(16, int(min(self.card.width, self.card.height) * 0.03))
        btn_h = max(42, int(self.card.height * 0.12))
        gap = max(10, int(self.card.width * 0.015))
        row_y = self.card.bottom - pad - btn_h
        grade_y = row_y - btn_h - gap

        btn_w = int((self.card.width - (2 * pad) - (2 * gap)) / 3)
        self.reveal_btn.set_rect(self.card.x + pad, row_y, btn_w, btn_h)
        self.next_btn.set_rect(self.card.x + pad + btn_w + gap, row_y, btn_w, btn_h)
        self.hint_btn.set_rect(self.card.x + pad + 2 * (btn_w + gap), row_y, btn_w, btn_h)

        grade_w = int((self.card.width - (2 * pad) - gap) / 2)
        self.correct_btn.set_rect(self.card.x + pad, grade_y, grade_w, btn_h)
        self.incorrect_btn.set_rect(self.card.x + pad + grade_w + gap, grade_y, grade_w, btn_h)

        if self.finished:
            two_w = int((self.card.width - (2 * pad) - gap) / 2)
            self.restart_btn.set_rect(self.card.x + pad, row_y, two_w, btn_h)
            self.close_btn.set_rect(self.card.x + pad + two_w + gap, row_y, two_w, btn_h)
        else:
            self.restart_btn.set_rect(self.card.x + pad, row_y, btn_w, btn_h)
            self.close_btn.set_rect(self.card.x + pad + btn_w + gap, row_y, btn_w, btn_h)

        list_x = self.card.x + pad
        list_y = self.card.y + pad + 48
        list_w = int(self.card.width * 0.35)
        list_h = self.card.height - (2 * pad) - 100
        self.edit_list_rect = pygame.Rect(list_x, list_y, list_w, list_h)

        right_x = list_x + list_w + gap
        right_w = self.card.right - pad - right_x
        input_h = max(42, int(self.card.height * 0.09))
        self.q_input.set_rect(right_x, list_y + 18, right_w, input_h)
        self.a_input.set_rect(right_x, list_y + 18 + input_h + 50, right_w, input_h)
        self.h_input.set_rect(right_x, list_y + 18 + (input_h + 50) * 2, right_w, input_h)

        edit_btn_w = int((right_w - gap) / 2)
        edit_btn_y = self.card.bottom - pad - btn_h
        self.add_btn.set_rect(right_x, edit_btn_y, edit_btn_w, btn_h)
        self.delete_btn.set_rect(right_x + edit_btn_w + gap, edit_btn_y, edit_btn_w, btn_h)

    def draw_play(self):
        pygame.draw.rect(self.screen, CARD, self.card, border_radius=14)
        pad = max(16, int(min(self.card.width, self.card.height) * 0.03))
        text_x = self.card.x + pad
        text_w = self.card.width - 2 * pad

        title = self.font_title.render("Quiz Software", True, TEXT)
        self.screen.blit(title, (text_x, self.card.y + pad))
        py = self.card.y + pad + title.get_height() + 10

        if not self.order:
            msg = self.font_text.render("No questions. Press Edit to add some.", True, MUTED)
            self.screen.blit(msg, (text_x, py + 30))
            return

        if self.finished:
            p = self.font_small.render("Completed", True, MUTED)
            self.screen.blit(p, (text_x, py))
            y = py + p.get_height() + 16
            for line in self.wrap_text("Game over. Every question has been used once.", self.font_text, text_w):
                surf = self.font_text.render(line, True, TEXT)
                self.screen.blit(surf, (text_x, y))
                y += self.font_text.get_linesize() + 8
            score = self.font_text.render(f"You got {self.score} out of {len(self.order)}", True, PRIMARY)
            self.screen.blit(score, (text_x, y + 12))
            return

        progress = self.font_small.render(
            f"Question {self.index + 1} of {len(self.order)}", True, MUTED
        )
        self.screen.blit(progress, (text_x, py))

        q = self.order[self.index]["q"]
        y = py + progress.get_height() + 18
        for line in self.wrap_text(q, self.font_text, text_w):
            surf = self.font_text.render(line, True, TEXT)
            self.screen.blit(surf, (text_x, y))
            y += self.font_text.get_linesize() + 6

        if self.show_answer:
            answer_top = y + 12
            controls_top = self.correct_btn.rect.y if self.correct_btn.visible else self.reveal_btn.rect.y
            max_h = max(56, controls_top - answer_top - 12)
            box = pygame.Rect(text_x, answer_top, text_w, max_h)
            pygame.draw.rect(self.screen, ANSWER_BG, box, border_radius=10)
            answer = f"Answer: {self.order[self.index]['a']}"
            ay = box.y + 12
            for line in self.wrap_text(answer, self.font_small, box.width - 20):
                surf = self.font_small.render(line, True, ANSWER_TEXT)
                self.screen.blit(surf, (box.x + 10, ay))
                ay += self.font_small.get_linesize() + 4
            if self.feedback_text:
                fb = self.font_small.render(self.feedback_text, True, MUTED)
                self.screen.blit(fb, (text_x, self.correct_btn.rect.y - fb.get_height() - 6))

        if self.show_hint:
            hint = self.order[self.index].get("h", "").strip() or "hint here"
            hs = self.font_small.render(f"Hint: {hint}", True, MUTED)
            self.screen.blit(hs, (text_x, self.reveal_btn.rect.y - hs.get_height() - 8))

    def draw_edit(self, mouse_pos):
        pygame.draw.rect(self.screen, CARD, self.card, border_radius=14)
        pad = max(16, int(min(self.card.width, self.card.height) * 0.03))
        title = self.font_title.render("Edit Questions", True, TEXT)
        self.screen.blit(title, (self.card.x + pad, self.card.y + pad))

        pygame.draw.rect(self.screen, INPUT_BG, self.edit_list_rect, border_radius=8)
        pygame.draw.rect(self.screen, INPUT_BORDER, self.edit_list_rect, 2, border_radius=8)

        line_h = self.font_small.get_linesize() + 8
        start_y = self.edit_list_rect.y + 10
        for i, item in enumerate(self.questions):
            row = pygame.Rect(
                self.edit_list_rect.x + 8,
                start_y + i * line_h,
                self.edit_list_rect.width - 16,
                line_h - 2,
            )
            if row.bottom > self.edit_list_rect.bottom - 4:
                break
            if i == self.selected_idx:
                pygame.draw.rect(self.screen, SECONDARY, row, border_radius=6)
            label = item.get("q", "").strip() or "(empty question)"
            if len(label) > 34:
                label = label[:31] + "..."
            txt = self.font_small.render(f"{i + 1}. {label}", True, TEXT)
            self.screen.blit(txt, (row.x + 6, row.y + 2))

        if not self.questions:
            empty = self.font_small.render("No questions yet. Click Add New.", True, MUTED)
            self.screen.blit(empty, (self.edit_list_rect.x + 10, self.edit_list_rect.y + 12))

        for inp in self.editor_inputs:
            inp.draw(self.screen, self.font_small, self.font_text)

        self.add_btn.draw(self.screen, self.font_btn, mouse_pos)
        self.delete_btn.draw(self.screen, self.font_btn, mouse_pos)

    def handle_edit_click_select(self, pos):
        if not self.edit_list_rect.collidepoint(pos):
            return
        line_h = self.font_small.get_linesize() + 8
        rel_y = pos[1] - (self.edit_list_rect.y + 10)
        idx = rel_y // line_h
        if 0 <= idx < len(self.questions):
            self.save_inputs_to_selected()
            self.selected_idx = idx
            self.load_selected_into_inputs()

    def run(self):
        while True:
            self.update_layout()
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
                    self.window_size = (max(700, event.w), max(460, event.h))
                    self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
                    self.update_layout()

                if self.toggle_mode_btn.clicked(event):
                    self.toggle_mode()
                if self.fullscreen_btn.clicked(event):
                    self.toggle_fullscreen()

                if self.mode == "play":
                    if self.reveal_btn.clicked(event):
                        self.reveal_answer()
                    elif self.next_btn.clicked(event):
                        self.next_question()
                    elif self.hint_btn.clicked(event):
                        self.reveal_hint()
                    elif self.correct_btn.clicked(event):
                        self.mark_answer(True)
                    elif self.incorrect_btn.clicked(event):
                        self.mark_answer(False)
                    elif self.restart_btn.clicked(event):
                        self.start_play_mode()
                    elif self.close_btn.clicked(event):
                        pygame.quit()
                        sys.exit(0)
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.handle_edit_click_select(event.pos)
                    for inp in self.editor_inputs:
                        if inp.handle_event(event):
                            self.save_inputs_to_selected()
                    if self.add_btn.clicked(event):
                        self.add_question()
                    if self.delete_btn.clicked(event):
                        self.delete_selected()

            self.screen.fill(BG)
            if self.mode == "play":
                self.draw_play()
                self.reveal_btn.draw(self.screen, self.font_btn, mouse_pos)
                self.next_btn.draw(self.screen, self.font_btn, mouse_pos)
                self.hint_btn.draw(self.screen, self.font_btn, mouse_pos)
                self.correct_btn.draw(self.screen, self.font_btn, mouse_pos)
                self.incorrect_btn.draw(self.screen, self.font_btn, mouse_pos)
                self.restart_btn.draw(self.screen, self.font_btn, mouse_pos)
                self.close_btn.draw(self.screen, self.font_btn, mouse_pos)
            else:
                self.draw_edit(mouse_pos)

            self.toggle_mode_btn.draw(self.screen, self.font_small, mouse_pos)
            self.fullscreen_btn.draw(self.screen, self.font_small, mouse_pos)

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    QuizApp().run()
