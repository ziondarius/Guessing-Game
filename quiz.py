import random
import sys

import pygame


QUESTIONS = [
    {"q": "What comes after 1?", "a": "2"},
    {"q": 'What part of speech is "me"?', "a": "pron."},
    {"q": "What famous tower is in Paris?", "a": "Eiffel Tower"},
    {"q": "What fruit do you get from an orange tree?", "a": "Orange"},
]

WIDTH, HEIGHT = 800, 480
BG = (241, 245, 249)
CARD = (255, 255, 255)
TEXT = (17, 24, 39)
MUTED = (75, 85, 99)
PRIMARY = (15, 118, 110)
PRIMARY_HOVER = (17, 94, 89)
SECONDARY = (229, 231, 235)
SECONDARY_HOVER = (209, 213, 219)
ANSWER_BG = (236, 253, 245)
ANSWER_TEXT = (6, 95, 70)


class Button:
    def __init__(self, x, y, w, h, label, kind="secondary"):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.kind = kind
        self.visible = True
        self.enabled = True

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
        txt_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, txt_rect)

    def clicked(self, event):
        return (
            self.visible
            and self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def set_rect(self, x, y, w, h):
        self.rect.update(int(x), int(y), int(w), int(h))


class QuizGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Quiz Software")
        self.is_fullscreen = False
        self.window_size = (WIDTH, HEIGHT)
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        self.font_title = None
        self.font_text = None
        self.font_small = None
        self.font_btn = None
        self.current_scale_key = None
        self.update_fonts()

        self.reveal_btn = Button(70, 390, 180, 52, "Reveal Answer", kind="primary")
        self.next_btn = Button(270, 390, 180, 52, "Next Question")
        self.hint_btn = Button(470, 390, 130, 52, "Hint")
        self.correct_btn = Button(70, 325, 180, 48, "Correct", kind="primary")
        self.incorrect_btn = Button(270, 325, 180, 48, "Incorrect")
        self.restart_btn = Button(470, 390, 130, 52, "Restart")
        self.close_btn = Button(470, 390, 130, 52, "Close")
        self.fullscreen_btn = Button(640, 15, 140, 38, "Fullscreen")

        self.start_game()

    def start_game(self):
        self.order = QUESTIONS[:]
        random.shuffle(self.order)
        self.index = 0
        self.score = 0
        self.marked_answers = [None] * len(self.order)
        self.show_answer = False
        self.show_hint = False
        self.feedback_text = ""
        self.finished = False

        self.reveal_btn.visible = True
        self.reveal_btn.enabled = True
        self.next_btn.visible = True
        self.next_btn.enabled = False
        self.hint_btn.visible = True
        self.hint_btn.enabled = True
        self.correct_btn.visible = False
        self.correct_btn.enabled = True
        self.incorrect_btn.visible = False
        self.incorrect_btn.enabled = True
        self.restart_btn.visible = False
        self.close_btn.visible = False

    def reveal_answer(self):
        if self.finished:
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
        if self.finished:
            return
        self.show_hint = True

    def mark_answer(self, is_correct):
        if self.finished or not self.show_answer:
            return
        if self.marked_answers[self.index] is not None:
            return

        self.marked_answers[self.index] = is_correct
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
            self.correct_btn.enabled = True
            self.incorrect_btn.enabled = True

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

    def update_fonts(self):
        width, height = self.screen.get_size()
        scale_key = int(min(width, height))
        if scale_key == self.current_scale_key:
            return
        self.current_scale_key = scale_key
        base = min(width, height)
        self.font_title = pygame.font.SysFont("arial", max(26, int(base * 0.055)), bold=True)
        self.font_text = pygame.font.SysFont("arial", max(20, int(base * 0.04)))
        self.font_small = pygame.font.SysFont("arial", max(16, int(base * 0.03)))
        self.font_btn = pygame.font.SysFont("arial", max(18, int(base * 0.033)))

    def update_layout(self):
        self.update_fonts()
        width, height = self.screen.get_size()
        card_w = int(width * 0.88)
        card_h = int(height * 0.84)
        card_x = (width - card_w) // 2
        card_y = (height - card_h) // 2
        self.card = pygame.Rect(card_x, card_y, card_w, card_h)

        pad = max(16, int(min(card_w, card_h) * 0.035))
        btn_h = max(44, int(card_h * 0.13))
        btn_gap = max(10, int(card_w * 0.02))
        row_y = self.card.bottom - pad - btn_h
        grade_row_y = row_y - btn_h - btn_gap

        btn_w = int((card_w - (pad * 2) - (btn_gap * 2)) / 3)
        self.reveal_btn.set_rect(card_x + pad, row_y, btn_w, btn_h)
        self.next_btn.set_rect(card_x + pad + btn_w + btn_gap, row_y, btn_w, btn_h)
        self.hint_btn.set_rect(card_x + pad + 2 * (btn_w + btn_gap), row_y, btn_w, btn_h)
        grade_w = int((card_w - (pad * 2) - btn_gap) / 2)
        self.correct_btn.set_rect(card_x + pad, grade_row_y, grade_w, btn_h)
        self.incorrect_btn.set_rect(card_x + pad + grade_w + btn_gap, grade_row_y, grade_w, btn_h)
        self.restart_btn.set_rect(card_x + pad + 2 * (btn_w + btn_gap), row_y, btn_w, btn_h)
        self.close_btn.set_rect(card_x + pad + 2 * (btn_w + btn_gap), row_y, btn_w, btn_h)

        if self.finished:
            two_w = int((card_w - (pad * 2) - btn_gap) / 2)
            self.restart_btn.set_rect(card_x + pad, row_y, two_w, btn_h)
            self.close_btn.set_rect(card_x + pad + two_w + btn_gap, row_y, two_w, btn_h)

        top_btn_w = max(130, int(width * 0.16))
        top_btn_h = max(34, int(height * 0.07))
        self.fullscreen_btn.set_rect(
            width - top_btn_w - 16,
            12,
            top_btn_w,
            top_btn_h,
        )

    def draw_card(self):
        card = self.card
        pygame.draw.rect(self.screen, CARD, card, border_radius=14)

        pad = max(16, int(min(card.width, card.height) * 0.035))
        text_x = card.x + pad
        text_w = card.width - (2 * pad)

        title = self.font_title.render("Quiz Software", True, TEXT)
        title_y = card.y + pad
        self.screen.blit(title, (text_x, title_y))

        progress_y = title_y + title.get_height() + max(10, int(card.height * 0.02))

        if self.finished:
            progress = self.font_small.render("Completed", True, MUTED)
            self.screen.blit(progress, (text_x, progress_y))
            msg = "Game over. Every question has been used once."
            y = progress_y + progress.get_height() + max(14, int(card.height * 0.03))
            line_gap = max(8, int(self.font_text.get_linesize() * 0.22))
            for line in self.wrap_text(msg, self.font_text, text_w):
                txt = self.font_text.render(line, True, TEXT)
                self.screen.blit(txt, (text_x, y))
                y += self.font_text.get_linesize() + line_gap
            score_text = f"You got {self.score} out of {len(self.order)}"
            score_surface = self.font_text.render(score_text, True, PRIMARY)
            self.screen.blit(score_surface, (text_x, y + max(8, int(card.height * 0.02))))
            return

        progress = self.font_small.render(
            f"Question {self.index + 1} of {len(self.order)}", True, MUTED
        )
        self.screen.blit(progress, (text_x, progress_y))

        q = self.order[self.index]["q"]
        y = progress_y + progress.get_height() + max(14, int(card.height * 0.03))
        line_gap = max(8, int(self.font_text.get_linesize() * 0.2))
        for line in self.wrap_text(q, self.font_text, text_w):
            txt = self.font_text.render(line, True, TEXT)
            self.screen.blit(txt, (text_x, y))
            y += self.font_text.get_linesize() + line_gap

        if self.show_answer:
            answer_top = y + max(10, int(card.height * 0.02))
            answer_h = max(72, int(card.height * 0.2))
            controls_top = self.correct_btn.rect.y if self.correct_btn.visible else self.reveal_btn.rect.y
            max_bottom = controls_top - max(10, int(card.height * 0.02))
            answer_h = max(56, min(answer_h, max_bottom - answer_top))
            answer_box = pygame.Rect(text_x, answer_top, text_w, answer_h)
            pygame.draw.rect(self.screen, ANSWER_BG, answer_box, border_radius=10)
            a = f'Answer: {self.order[self.index]["a"]}'
            ay = answer_box.y + max(10, int(answer_box.height * 0.18))
            for line in self.wrap_text(a, self.font_small, answer_box.width - 20):
                txt = self.font_small.render(line, True, ANSWER_TEXT)
                self.screen.blit(txt, (answer_box.x + 10, ay))
                ay += self.font_small.get_linesize() + 6

            if self.feedback_text:
                feedback = self.font_small.render(self.feedback_text, True, MUTED)
                fy = self.correct_btn.rect.y - feedback.get_height() - max(6, int(card.height * 0.01))
                self.screen.blit(feedback, (text_x, fy))

        if self.show_hint:
            hint = self.font_small.render("Hint: hint here", True, MUTED)
            hint_y = self.reveal_btn.rect.y - hint.get_height() - max(8, int(card.height * 0.02))
            self.screen.blit(hint, (text_x, hint_y))

    def run(self):
        while True:
            self.update_layout()
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
                    self.window_size = (max(640, event.w), max(400, event.h))
                    self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
                    self.update_layout()
                if self.fullscreen_btn.clicked(event):
                    self.toggle_fullscreen()
                if self.reveal_btn.clicked(event):
                    self.reveal_answer()
                if self.next_btn.clicked(event):
                    self.next_question()
                if self.hint_btn.clicked(event):
                    self.reveal_hint()
                if self.correct_btn.clicked(event):
                    self.mark_answer(True)
                if self.incorrect_btn.clicked(event):
                    self.mark_answer(False)
                if self.restart_btn.clicked(event):
                    self.start_game()
                if self.close_btn.clicked(event):
                    pygame.quit()
                    sys.exit(0)

            self.screen.fill(BG)
            self.draw_card()
            self.fullscreen_btn.draw(self.screen, self.font_small, mouse_pos)
            self.reveal_btn.draw(self.screen, self.font_btn, mouse_pos)
            self.next_btn.draw(self.screen, self.font_btn, mouse_pos)
            self.hint_btn.draw(self.screen, self.font_btn, mouse_pos)
            self.correct_btn.draw(self.screen, self.font_btn, mouse_pos)
            self.incorrect_btn.draw(self.screen, self.font_btn, mouse_pos)
            self.restart_btn.draw(self.screen, self.font_btn, mouse_pos)
            self.close_btn.draw(self.screen, self.font_btn, mouse_pos)

            pygame.display.flip()
            self.clock.tick(60)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.window_size = self.screen.get_size()
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.fullscreen_btn.label = "Windowed"
        else:
            self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
            self.fullscreen_btn.label = "Fullscreen"
        self.update_layout()


if __name__ == "__main__":
    QuizGame().run()
