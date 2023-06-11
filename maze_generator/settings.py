import pygame


class SettingsPage:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 30)
        self.options = {
            "Algorithm": {0: "A*", 1: "DFS"},
            "Auto-play": {1: True, 0: False, },
        }
        self.values = {
            "Algorithm": list(self.options["Algorithm"].keys())[0],
            "Auto-play": list(self.options["Auto-play"].keys())[0],
        }
        self.labels = []
        for i, (key, value) in enumerate(self.options.items()):
            label = self.font.render(f"{key}: {value[self.values[key]]}", True, (255, 255, 255))
            label_rect = label.get_rect()
            label_rect.center = (200, 100 + i * 100)
            self.labels.append((key, label, label_rect))
        self.start_button = self.font.render("Start Game", True, (255, 255, 255))
        self.start_button_rect = self.start_button.get_rect()
        self.start_button_rect.center = (400, 500)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if self.start_button_rect.collidepoint(pos):
                        return self.values
                    for key, label, label_rect in self.labels:
                        if label_rect.collidepoint(pos):
                            self.values[key] = (self.values[key] + 1) % len(self.options[key])

            self.screen.fill((0, 0, 0))
            for i, (key, label, label_rect) in enumerate(self.labels):
                label = self.font.render(f"{key}: {self.options[key][self.values[key]]}", True, (255, 255, 255))
                label_rect = label.get_rect()
                label_rect.center = (200, 100 + i * 100)
                self.labels[i] = (key, label, label_rect)
                self.screen.blit(label, label_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), self.start_button_rect, 2)
            self.screen.blit(self.start_button, self.start_button_rect)
            pygame.display.flip()