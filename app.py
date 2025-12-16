from flask import Flask, render_template, request, jsonify
from solve import GridMap, AStarSolver, MazeArchitect, TerrainType

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    try:
        data = request.json
        raw_grid = data.get('grid', [])
        start_node = tuple(data.get('start', []))
        end_node = tuple(data.get('end', []))

        # 1. Khởi tạo bản đồ
        grid_map = GridMap(raw_grid)
        
        # 2. Khởi tạo thuật toán
        solver = AStarSolver(grid_map)
        
        # 3. Chạy và lấy kết quả
        path, visited = solver.solve(start_node, end_node)
        
        return jsonify({'path': path, 'visited': visited})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/generate_maze', methods=['POST'])
def generate_maze():
    data = request.json
    rows = data.get('rows', 21)
    cols = data.get('cols', 21)
    
    # Sử dụng Static Method của MazeArchitect
    maze = MazeArchitect.generate_dfs(rows, cols)
    
    # Thiết lập điểm đầu cuối mặc định
    start = [1, 1]
    end = [rows-2, cols-2]
    
    # Đảm bảo điểm đầu cuối không bị lấp
    maze[start[0]][start[1]] = TerrainType.EMPTY
    maze[end[0]][end[1]] = TerrainType.EMPTY
    
    return jsonify({'grid': maze, 'start': start, 'end': end})

if __name__ == '__main__':
    app.run(debug=True)