import heapq
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Set, Optional

# --- CẤU HÌNH HẰNG SỐ (CONSTANTS) ---
class TerrainType:
    EMPTY = 0
    WALL = 1
    WATER = 2

class MovementCost:
    DEFAULT = 1
    WATER = 5

# --- LỚP QUẢN LÝ BẢN ĐỒ ---
class GridMap:
    """Quản lý thông tin và logic của bản đồ."""
    def __init__(self, raw_grid: List[List[int]]):
        self.grid = raw_grid
        self.rows = len(raw_grid)
        self.cols = len(raw_grid[0]) if self.rows > 0 else 0

    def is_within_bounds(self, r: int, c: int) -> bool:
        """Kiểm tra tọa độ có nằm trong lưới không."""
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_walkable(self, r: int, c: int) -> bool:
        """Kiểm tra ô đó có đi được không (không phải tường)."""
        return self.is_within_bounds(r, c) and self.grid[r][c] != TerrainType.WALL

    def get_cost(self, r: int, c: int) -> int:
        """Lấy chi phí di chuyển vào ô (r, c)."""
        if self.grid[r][c] == TerrainType.WATER:
            return MovementCost.WATER
        return MovementCost.DEFAULT

    def get_neighbors(self, node: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Trả về danh sách các ô lân cận hợp lệ (4 hướng)."""
        r, c = node
        # Hướng: Lên, Xuống, Trái, Phải
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        valid_neighbors = []
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if self.is_walkable(nr, nc):
                valid_neighbors.append((nr, nc))
        
        return valid_neighbors

# --- LỚP THUẬT TOÁN A* ---
class AStarSolver:
    """Thực thi thuật toán tìm đường A*."""
    
    def __init__(self, grid_map: GridMap):
        self.map = grid_map

    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Tính khoảng cách Manhattan."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _reconstruct_path(self, came_from: Dict, current: Tuple) -> List[Tuple]:
        """Truy vết ngược lại để tạo đường đi."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def solve(self, start: Tuple[int, int], end: Tuple[int, int]) -> Tuple[List, List]:
        """
        Hàm chính để chạy thuật toán.
        Trả về: (path, visited_order)
        """
        # Priority Queue lưu: (f_score, insertion_order, node)
        open_set = []
        heapq.heappush(open_set, (0, 0, start))
        
        came_from: Dict[Tuple, Tuple] = {}
        
        # G_score: Chi phí thực từ start
        g_score: Dict[Tuple, float] = {start: 0}
        
        # F_score: G_score + Heuristic
        f_score: Dict[Tuple, float] = {start: self._heuristic(start, end)}
        
        open_set_hash: Set[Tuple] = {start}
        visited_order: List[Tuple] = []
        count = 0 

        while open_set:
            current = heapq.heappop(open_set)[2]
            open_set_hash.remove(current)
            visited_order.append(current)

            if current == end:
                return self._reconstruct_path(came_from, end), visited_order

            for neighbor in self.map.get_neighbors(current):
                # Tính toán chi phí mới: G_current + Cost_neighbor
                new_g_score = g_score[current] + self.map.get_cost(*neighbor)

                if new_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = new_g_score
                    f_score[neighbor] = new_g_score + self._heuristic(neighbor, end)
                    
                    if neighbor not in open_set_hash:
                        count += 1
                        heapq.heappush(open_set, (f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)

        return [], visited_order

# --- LỚP TẠO MÊ CUNG ---
class MazeArchitect:
    """Chuyên trách việc tạo bản đồ/mê cung."""
    
    @staticmethod
    def generate_dfs(rows: int, cols: int) -> List[List[int]]:
        """Tạo mê cung bằng thuật toán DFS Backtracking."""
        # Khởi tạo full tường
        grid = [[TerrainType.WALL for _ in range(cols)] for _ in range(rows)]
        
        # Điểm bắt đầu thuật toán (thường thụt vào 1 ô để có viền)
        start_r, start_c = 1, 1
        grid[start_r][start_c] = TerrainType.EMPTY
        
        stack = [(start_r, start_c)]
        
        while stack:
            r, c = stack[-1]
            neighbors = []
            
            # Tìm hàng xóm cách 2 bước (để chừa tường ở giữa)
            directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
            
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 < nr < rows - 1 and 0 < nc < cols - 1 and grid[nr][nc] == TerrainType.WALL:
                    neighbors.append((nr, nc, dr, dc))
            
            if neighbors:
                nr, nc, dr, dc = random.choice(neighbors)
                # Đục tường ngăn cách
                grid[r + dr // 2][c + dc // 2] = TerrainType.EMPTY
                # Đục ô đích
                grid[nr][nc] = TerrainType.EMPTY
                stack.append((nr, nc))
            else:
                stack.pop()
                
        return grid