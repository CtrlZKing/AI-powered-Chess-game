import pygame
import chess
import sys
import subprocess
import os
import random

# --- AI CONFIGURATION ---
ENGINE_NAME = "stockfish.exe"

# Configuration
WIDTH, HEIGHT = 600, 600
SQ_SIZE = WIDTH // 8
WHITE_COLOR = (245, 245, 220)
GREEN_COLOR = (119, 149, 86)
HIGHLIGHT_COLOR = (186, 202, 68)
MOVE_GLOW_COLOR = (255, 255, 100)

# Piece Colors
COLOR_WHITE = (255, 255, 255)
COLOR_WHITE_SHADOW = (210, 210, 210)
COLOR_BLACK = (30, 30, 30)
COLOR_BLACK_LIGHT = (60, 60, 60)
OUTLINE = (0, 0, 0)

def get_ai_move(board):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, ENGINE_NAME)
        process = subprocess.Popen(
            path, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            universal_newlines=True, bufsize=1, creationflags=0x08000000 
        )
        process.stdin.write(f"uci\nposition fen {board.fen()}\ngo movetime 1000\n")
        process.stdin.flush()
        while True:
            line = process.stdout.readline().strip()
            if line.startswith("bestmove"):
                move_uci = line.split()[1]
                process.terminate()
                return chess.Move.from_uci(move_uci)
    except Exception:
        return None

def draw_piece(screen, piece, x, y, custom_sq=SQ_SIZE):
    center_x = x + custom_sq // 2
    base_y = y + custom_sq - 10
    is_white = piece.color == chess.WHITE
    main_c = COLOR_WHITE if is_white else COLOR_BLACK
    shad_c = COLOR_WHITE_SHADOW if is_white else COLOR_BLACK_LIGHT
    
    def draw_complex_shape(points):
        pygame.draw.polygon(screen, shad_c, points)
        half_points = [(px, py) if px > center_x else (center_x, py) for px, py in points]
        pygame.draw.polygon(screen, main_c, half_points)
        pygame.draw.polygon(screen, OUTLINE, points, 2)

    def draw_base(width_val):
        for i, w in enumerate([width_val, width_val-10]):
            rect = (center_x - w//2, base_y - (i*6), w, 8)
            pygame.draw.rect(screen, shad_c, rect, border_radius=2)
            pygame.draw.rect(screen, OUTLINE, rect, 2, border_radius=2)

    if piece.piece_type == chess.PAWN:
        draw_base(34)
        pts = [(center_x-8, base_y-12), (center_x+8, base_y-12), (center_x+5, y+35), (center_x-5, y+35)]
        draw_complex_shape(pts)
        pygame.draw.circle(screen, main_c, (center_x, y+30), 10)
        pygame.draw.circle(screen, OUTLINE, (center_x, y+30), 10, 2)
    elif piece.piece_type == chess.ROOK:
        draw_base(42)
        pts = [(center_x-14, base_y-12), (center_x+14, base_y-12), (center_x+12, base_y-25), (center_x-12, base_y-25)]
        draw_complex_shape(pts)
        pts_top = [(center_x-12, base_y-25), (center_x+12, base_y-25), (center_x+15, y+20), (center_x-15, y+20)]
        draw_complex_shape(pts_top)
        pygame.draw.rect(screen, main_c, (center_x-17, y+10, 34, 12))
        pygame.draw.rect(screen, OUTLINE, (center_x-17, y+10, 34, 12), 2)
        for bx in [center_x-12, center_x, center_x+12]:
            pygame.draw.line(screen, OUTLINE, (bx, y+10), (bx, y+15), 2)
    elif piece.piece_type == chess.KNIGHT:
        draw_base(40)
        pts = [(center_x - 12, base_y - 12), (center_x + 12, base_y - 12), (center_x + 14, y + 45), (center_x + 20, y + 30), (center_x + 18, y + 15), (center_x + 8, y + 8), (center_x - 4, y + 12), (center_x - 18, y + 22), (center_x - 20, y + 32), (center_x - 10, y + 38), (center_x - 6, y + 45)]
        draw_complex_shape(pts)
        eye_c = (0,0,0) if is_white else (255,255,255)
        pygame.draw.circle(screen, eye_c, (center_x - 7, y + 22), 2)
    elif piece.piece_type == chess.BISHOP:
        draw_base(38)
        pts = [(center_x-10, base_y-12), (center_x+10, base_y-12), (center_x, y+15)]
        draw_complex_shape(pts)
        pygame.draw.ellipse(screen, main_c, (center_x-11, y+18, 22, 28))
        pygame.draw.ellipse(screen, OUTLINE, (center_x-11, y+18, 22, 28), 2)
        pygame.draw.circle(screen, main_c, (center_x, y+16), 4)
    elif piece.piece_type == chess.QUEEN:
        draw_base(44)
        pts = [(center_x-10, base_y-12), (center_x+10, base_y-12), (center_x+6, y+35), (center_x+14, y+25), (center_x-14, y+25), (center_x-6, y+35)]
        draw_complex_shape(pts)
        crown_pts = [(center_x-20, y+8), (center_x-10, y+18), (center_x, y+2), (center_x+10, y+18), (center_x+20, y+8), (center_x+12, y+25), (center_x-12, y+25)]
        draw_complex_shape(crown_pts)
        pygame.draw.circle(screen, main_c, (center_x, y+2), 5)
        pygame.draw.circle(screen, OUTLINE, (center_x, y+2), 5, 1)
    elif piece.piece_type == chess.KING:
        draw_base(42)
        pts = [(center_x-14, base_y-12), (center_x+14, base_y-12), (center_x+10, y+25), (center_x-10, y+25)]
        draw_complex_shape(pts)
        pygame.draw.rect(screen, main_c, (center_x-15, y+15, 30, 12), border_radius=2)
        pygame.draw.rect(screen, OUTLINE, (center_x-15, y+15, 30, 12), 2, border_radius=2)
        pygame.draw.line(screen, OUTLINE, (center_x, y+2), (center_x, y+15), 3)
        pygame.draw.line(screen, OUTLINE, (center_x-5, y+8), (center_x+5, y+8), 3)

def draw_menu(screen, selected_color):
    screen.fill((40, 44, 52))
    font_title = pygame.font.SysFont("georgia", 64, bold=True)
    font_button = pygame.font.SysFont("verdana", 24)
    title_surf = font_title.render("My_Chess.py", True, WHITE_COLOR)
    title_rect = title_surf.get_rect(center=(WIDTH//2, 120))
    screen.blit(title_surf, title_rect)
    btn_pass = pygame.Rect(WIDTH//2 - 125, 250, 250, 60)
    btn_ai = pygame.Rect(WIDTH//2 - 125, 330, 250, 60)
    box_white = pygame.Rect(WIDTH//2 - 90, 430, 80, 80)
    box_black = pygame.Rect(WIDTH//2 + 10, 430, 80, 80)
    for btn, text in [(btn_pass, "Pass and Play"), (btn_ai, "Play AI")]:
        pygame.draw.rect(screen, GREEN_COLOR, btn, border_radius=10)
        pygame.draw.rect(screen, OUTLINE, btn, 3, border_radius=10)
        txt_surf = font_button.render(text, True, COLOR_BLACK)
        screen.blit(txt_surf, txt_surf.get_rect(center=btn.center))
    pygame.draw.rect(screen, (60, 60, 60), box_white, border_radius=5)
    pygame.draw.rect(screen, (60, 60, 60), box_black, border_radius=5)
    if selected_color == chess.WHITE:
        pygame.draw.rect(screen, MOVE_GLOW_COLOR, box_white, 4, border_radius=5)
    elif selected_color == chess.BLACK:
        pygame.draw.rect(screen, MOVE_GLOW_COLOR, box_black, 4, border_radius=5)
    draw_piece(screen, chess.Piece(chess.KING, chess.WHITE), box_white.x, box_white.y, 80)
    draw_piece(screen, chess.Piece(chess.KING, chess.BLACK), box_black.x, box_black.y, 80)
    return btn_pass, btn_ai, box_white, box_black

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("My_Chess.py")
    board = chess.Board()
    selected_square = None
    last_move = None
    menu_active = True
    use_ai = False
    chosen_color = None 
    
    # Font for end game message
    font_end = pygame.font.SysFont("impact", 72)
    
    while True:
        if menu_active:
            btn_pass, btn_ai, box_w, box_b = draw_menu(screen, chosen_color)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if box_w.collidepoint(event.pos): chosen_color = chess.WHITE
                    if box_b.collidepoint(event.pos): chosen_color = chess.BLACK
                    if btn_pass.collidepoint(event.pos):
                        use_ai = False
                        if chosen_color is None: chosen_color = chess.WHITE
                        menu_active = False
                    if btn_ai.collidepoint(event.pos):
                        use_ai = True
                        if chosen_color is None: chosen_color = random.choice([chess.WHITE, chess.BLACK])
                        menu_active = False
            pygame.display.flip()
            continue

        if not board.is_game_over() and use_ai and board.turn != chosen_color:
            move = get_ai_move(board)
            if move:
                last_move = move
                board.push(move)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not use_ai or (use_ai and board.turn == chosen_color):
                    pos = pygame.mouse.get_pos()
                    c, r = pos[0] // SQ_SIZE, pos[1] // SQ_SIZE
                    # Flip coordinates if playing as Black
                    if chosen_color == chess.BLACK:
                        col, row = 7 - c, r
                    else:
                        col, row = c, 7 - r
                    clicked_sq = chess.square(col, row)
                    if selected_square is None:
                        piece = board.piece_at(clicked_sq)
                        if piece and piece.color == board.turn:
                            selected_square = clicked_sq
                    else:
                        move = chess.Move(selected_square, clicked_sq)
                        if board.piece_at(selected_square) and board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_rank(clicked_sq) in [0, 7]:
                            move.promotion = chess.QUEEN
                        if move in board.legal_moves:
                            board.push(move)
                            last_move = move
                        selected_square = None

        for r in range(8):
            for c in range(8):
                if chosen_color == chess.BLACK:
                    sq = chess.square(7 - c, r)
                else:
                    sq = chess.square(c, 7 - r)
                
                color = WHITE_COLOR if (r + c) % 2 == 0 else GREEN_COLOR
                if last_move and (sq == last_move.from_square or sq == last_move.to_square):
                    color = MOVE_GLOW_COLOR
                if selected_square == sq:
                    color = HIGHLIGHT_COLOR
                
                pygame.draw.rect(screen, color, (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                piece = board.piece_at(sq)
                if piece:
                    draw_piece(screen, piece, c*SQ_SIZE, r*SQ_SIZE)

        # Checkmate Logic
        if board.is_checkmate():
            text_surf = font_end.render("CHECKMATE", True, (200, 0, 0))
            text_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
            # Draw a dark overlay behind the text for visibility
            overlay = pygame.Surface((WIDTH, 100))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, HEIGHT//2 - 50))
            screen.blit(text_surf, text_rect)
        elif board.is_check():
            font_small = pygame.font.SysFont("verdana", 20, bold=True)
            check_surf = font_small.render("CHECK!", True, (255, 140, 0))
            screen.blit(check_surf, (10, 10))

        pygame.display.flip()

if __name__ == "__main__":
    main()
