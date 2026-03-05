// 【A*算法优化完整版】：终点出队即停止，搜索效率更高
using Raylib_cs;
using System.Numerics;

internal enum MazeCellState { Path, Wall }

internal struct MazeCell { public MazeCellState State; }

internal struct PathInfo
{
    public int PrevRow;    // 前驱行
    public int PrevCol;    // 前驱列
    public int G_Distance; // 到起点的实际距离（g值）
    public int F_Score;    // 总评分（g + h）
}

internal struct DisplayText { public string Text; public Vector2 Position; public float RemainTime; }

internal struct BlinkNode { public (int row, int col) Cell; public float RemainTime; public float BlinkInterval; public float LastBlinkTime; public bool IsVisible; }

namespace AStarMazeVisualizer
{
    internal static class Program
    {
        // ===================== 基础常量 =====================
        private const int MapWidth = 800;
        private const int MapHeight = 800;
        private const int ControlBarHeight = 100;
        private const int WindowWidth = 800;
        private const int WindowHeight = 900;
        private const int CellSize = 20;
        private const int GridRows = MapHeight / CellSize;
        private const int GridCols = MapWidth / CellSize;
        private const int DotRadius = CellSize / 3;

        // ===================== 全局核心变量 =====================
        private static MazeCell[,] _mazeGrid;

        // ===================== 核心状态 =====================
        private static PriorityQueue<(int row, int col), int> _priorityQueue;
        private static HashSet<(int row, int col)> _visitedSet;
        private static (int row, int col) _currentProcessingCell;
        private static bool _isProcessing;
        private static List<(int row, int col)> _currentAdjacentCells;
        private static int _currentAdjIndex;
        private static float _animationTimer;
        private const float NormalAnimationSpeed = 1.0f;
        private const float AutoAnimationSpeed = 0.0625f;
        private static bool _isAutoRunning;
        private static bool _isAutoStopRequested;

        // ===================== 涂色常量 =====================
        private readonly static Color ColorWall = Color.Black;
        private readonly static Color ColorPath = Color.White;
        private readonly static Color ColorHeapTop = Color.Lime;
        private readonly static Color ColorAdjacent = Color.Green;
        private readonly static Color ColorVisited = new Color(180, 180, 180, 255);
        private readonly static Color ColorBlink = Color.Yellow;
        private readonly static Color ColorShortestPath = Color.Purple;
        private readonly static Color ColorHeuristic = new Color(255, 150, 150, 255);

        // ===================== 按钮与UI常量 =====================
        private const int ButtonWidth = 150;
        private const int ButtonHeight = 30;
        private const int ButtonY = 860;
        private const int ButtonAutoX = 320;
        private const int ButtonInitX = 480;
        private const int ButtonRunX = 640;

        // ===================== 最短路径相关状态 =====================
        private static (int row, int col) _endCell;
        private static List<(int row, int col)> _shortestPath;
        private static bool _isShortestPathCalculated;

        // ===================== 其他状态 =====================
        private static (int row, int col) _startCell;
        private static Vector2 _startPos;
        private static Vector2 _endPos;
        private static Dictionary<(int, int), PathInfo> _pathInfoTable;
        private static List<DisplayText> _displayTexts;
        private static List<BlinkNode> _blinkNodes;
        private static bool _isInitialized;
        private static bool _isButtonClickable;

        // ===================== A*新增：计算曼哈顿距离 =====================
        private static int ManhattanDistance((int row, int col) cell)
        {
            return Math.Abs(cell.row - _endCell.row) + Math.Abs(cell.col - _endCell.col);
        }

        // ===================== A*新增：计算F值 =====================
        private static int CalculateFScore(int g, (int row, int col) cell)
        {
            return g + ManhattanDistance(cell);
        }

        [System.STAThread]
        public static void Main()
        {
            // ===================== 1. 初始化迷宫 =====================
            _mazeGrid = new MazeCell[GridRows, GridCols];
            GenerateSimpleRandomMaze(_mazeGrid);
            _startPos = FindFirstEmptyCell(_mazeGrid);
            _endPos = FindLastEmptyCell(_mazeGrid);
            _startCell = ((int)(_startPos.Y / CellSize), (int)(_startPos.X / CellSize));
            _endCell = ((int)(_endPos.Y / CellSize), (int)(_endPos.X / CellSize));

            // ===================== 2. 初始化核心容器 =====================
            _priorityQueue = new PriorityQueue<(int row, int col), int>();
            _visitedSet = new HashSet<(int row, int col)>();
            _currentProcessingCell = (0, 0);
            _isProcessing = false;
            _currentAdjacentCells = new List<(int row, int col)>();
            _currentAdjIndex = 0;
            _animationTimer = 0.0f;
            _isAutoRunning = false;
            _isAutoStopRequested = false;

            // ===================== 3. 初始化最短路径状态 =====================
            _shortestPath = new List<(int row, int col)>();
            _isShortestPathCalculated = false;

            // ===================== 4. 初始化路径信息表 =====================
            _pathInfoTable = new Dictionary<(int, int), PathInfo>();
            InitPathInfoTable(_mazeGrid);

            // ===================== 5. 初始化UI状态 =====================
            _displayTexts = new List<DisplayText>();
            _blinkNodes = new List<BlinkNode>();
            _isInitialized = false;
            _isButtonClickable = false;

            // ===================== 6. 窗口初始化 =====================
            Raylib.InitWindow(WindowWidth, WindowHeight, "A*算法迷宫演示 - 终点出队即停止优化版");
            Raylib.SetTargetFPS(60);

            // ===================== 7. 主循环 =====================
            while (!Raylib.WindowShouldClose())
            {
                float deltaTime = Raylib.GetFrameTime();

                // -------------------- 7.1 更新计时器 --------------------
                UpdateTimers(deltaTime);

                // -------------------- 7.2 处理交互 --------------------
                HandleInput();

                // -------------------- 7.3 自动运行逻辑 --------------------
                HandleAutoRun();

                // -------------------- 7.4 执行动画步骤 --------------------
                if (_isProcessing)
                {
                    ProcessAdjacentNodeStep(deltaTime);
                }

                // -------------------- 7.5 绘制所有内容 --------------------
                Raylib.BeginDrawing();
                Raylib.ClearBackground(Color.RayWhite);

                DrawMazeGrid();          // 绘制迷宫（含最短路径）
                DrawDisplayTexts();      // 绘制路径比较文本
                Raylib.DrawCircleV(_startPos, DotRadius, Color.Red);   // 起点
                Raylib.DrawCircleV(_endPos, DotRadius, Color.Blue);    // 终点
                DrawControlBar();        // 绘制控制栏

                // 绘制按钮
                DrawButton(new Rectangle(ButtonAutoX, ButtonY, ButtonWidth, ButtonHeight),
                          _isAutoRunning ? "Stop Auto" : "Auto Run",
                          GetAutoButtonEnabledState());
                DrawButton(new Rectangle(ButtonInitX, ButtonY, ButtonWidth, ButtonHeight),
                          "Init Algorithm",
                          !_isProcessing && !_isAutoRunning);
                DrawButton(new Rectangle(ButtonRunX, ButtonY, ButtonWidth, ButtonHeight),
                          "Run Algorithm",
                          _isButtonClickable && !_isProcessing && !_isAutoRunning);

                Raylib.EndDrawing();
            }

            Raylib.CloseWindow();
        }

        // ===================== 计算自动按钮可用状态 =====================
        private static bool GetAutoButtonEnabledState()
        {
            if (_isAutoRunning)
            {
                return _isInitialized && !_visitedSet.Contains(_endCell);
            }
            else
            {
                return _isInitialized && !_isProcessing && !_visitedSet.Contains(_endCell);
            }
        }

        // ===================== 自动运行逻辑（优化版） =====================
        private static void HandleAutoRun()
        {
            // A*优化：如果终点已经找到，停止自动运行
            if (_visitedSet.Contains(_endCell))
            {
                _isAutoRunning = false;
                _isAutoStopRequested = false;
                if (!_isShortestPathCalculated)
                {
                    CalculateShortestPath();
                    _isShortestPathCalculated = true;
                }
                return;
            }

            // 自动运行开启 + 无停止请求 + 当前无处理中的动画 + 已初始化 + 队列非空 → 自动启动下一个
            if (_isAutoRunning && !_isAutoStopRequested && !_isProcessing && _isInitialized && _priorityQueue.Count > 0)
            {
                StartProcessingHeapTop();
            }
            // 有停止请求且当前无处理 → 重置自动运行状态
            else if (_isAutoStopRequested && !_isProcessing)
            {
                _isAutoRunning = false;
                _isAutoStopRequested = false;
                _currentProcessingCell = (0, 0);
            }
            // 队列为空（算法结束）→ 自动停止 + 计算并显示最短路径
            else if (_isAutoRunning && _priorityQueue.Count == 0 && !_isProcessing)
            {
                _isAutoRunning = false;
                _isAutoStopRequested = false;
                _currentProcessingCell = (0, 0);
                CalculateShortestPath();
                _isShortestPathCalculated = true;
            }
        }

        // ===================== 回溯计算最短路径 =====================
        private static void CalculateShortestPath()
        {
            _shortestPath.Clear();
            var currentCell = _endCell;

            while (true)
            {
                if (!_pathInfoTable.ContainsKey(currentCell)) break;
                var pathInfo = _pathInfoTable[currentCell];

                _shortestPath.Add(currentCell);

                if (pathInfo.PrevRow == -1 && pathInfo.PrevCol == -1) break;

                currentCell = (pathInfo.PrevRow, pathInfo.PrevCol);

                if (currentCell.row < 0 || currentCell.col < 0 ||
                    currentCell.row >= GridRows || currentCell.col >= GridCols)
                {
                    _shortestPath.Clear();
                    break;
                }
            }

            _shortestPath.Reverse();

            // 在控制台输出路径长度，便于观察算法效率
            if (_shortestPath.Count > 0)
            {
                Console.WriteLine($"A*找到最短路径，长度: {_shortestPath.Count - 1}步");
                Console.WriteLine($"已访问单元格数: {_visitedSet.Count}");
            }
            else
            {
                Console.WriteLine("A*未找到路径");
            }
        }

        // ===================== 核心函数：涂色逻辑 =====================
        private static Color GetCellColor(int row, int col)
        {
            if (_mazeGrid[row, col].State == MazeCellState.Wall)
            {
                return ColorWall;
            }

            var cell = (row, col);

            if (_isShortestPathCalculated && _shortestPath.Contains(cell))
            {
                return ColorShortestPath;
            }

            if (_visitedSet.Contains(cell))
            {
                return ColorVisited;
            }

            if (_isProcessing && cell == _currentProcessingCell)
            {
                return ColorHeapTop;
            }

            if (_isProcessing && IsAdjacent(_currentProcessingCell, cell) && !_visitedSet.Contains(cell))
            {
                return ColorAdjacent;
            }

            return ColorPath;
        }

        // ===================== 核心函数：启动堆顶处理（优化版） =====================
        private static void StartProcessingHeapTop()
        {
            if (_priorityQueue.Count == 0)
            {
                _isAutoRunning = false;
                _isAutoStopRequested = false;
                CalculateShortestPath();
                _isShortestPathCalculated = true;
                return;
            }

            var heapTop = _priorityQueue.UnorderedItems.OrderBy(item => item.Priority).First().Element;

            // A*优化：如果堆顶就是终点，直接结束算法
            if (heapTop == _endCell)
            {
                var dequeuedCell = _priorityQueue.Dequeue();
                _visitedSet.Add(dequeuedCell);

                _isAutoRunning = false;
                _isAutoStopRequested = false;
                CalculateShortestPath();
                _isShortestPathCalculated = true;
                Console.WriteLine($"终点作为堆顶直接出队！最短路径已找到。");
                return;
            }

            _currentProcessingCell = heapTop;
            _isProcessing = true;
            _isButtonClickable = false;

            _currentAdjacentCells = GetValidAdjacentCells(heapTop);
            _currentAdjIndex = 0;
            _animationTimer = 0.0f;
        }

        // ===================== 核心函数：处理邻接节点（优化版） =====================
        private static void ProcessAdjacentNodeStep(float deltaTime)
        {
            if (_currentAdjIndex >= _currentAdjacentCells.Count)
            {
                if (_priorityQueue.Count > 0)
                {
                    var dequeuedCell = _priorityQueue.Dequeue();
                    if (dequeuedCell == _currentProcessingCell)
                    {
                        _visitedSet.Add(dequeuedCell);

                        // A*优化：如果出队的是终点，立即停止算法
                        if (dequeuedCell == _endCell)
                        {
                            CalculateShortestPath();
                            _isShortestPathCalculated = true;
                            _isAutoRunning = false;
                            _isAutoStopRequested = false;
                            Console.WriteLine($"终点出队！最短路径已找到。");
                        }
                    }
                }

                _isProcessing = false;
                _isButtonClickable = true;
                _currentProcessingCell = (0, 0);
                return;
            }

            float currentSpeed = _isAutoRunning ? AutoAnimationSpeed : NormalAnimationSpeed;

            _animationTimer += deltaTime;
            if (_animationTimer < currentSpeed) return;

            var adjCell = _currentAdjacentCells[_currentAdjIndex];
            var topPathInfo = _pathInfoTable[_currentProcessingCell];

            int newG = topPathInfo.G_Distance + 1;
            var adjPathInfo = _pathInfoTable[adjCell];

            int newF = CalculateFScore(newG, adjCell);
            int oldF = adjPathInfo.F_Score;

            string compareText = oldF > newF
                ? $"F:{oldF} > {newF}"
                : $"F:{oldF} <= {newF}";
            AddDisplayText(compareText, adjCell);

            if (oldF > newF)
            {
                _pathInfoTable[adjCell] = new PathInfo
                {
                    PrevRow = _currentProcessingCell.row,
                    PrevCol = _currentProcessingCell.col,
                    G_Distance = newG,
                    F_Score = newF
                };

                _priorityQueue.Enqueue(adjCell, newF);
                AddBlinkNode(adjCell);
            }

            _currentAdjIndex++;
            _animationTimer = 0.0f;
        }

        // ===================== 交互处理 =====================
        private static void HandleInput()
        {
            Vector2 mousePos = Raylib.GetMousePosition();
            Rectangle btnAutoRect = new Rectangle(ButtonAutoX, ButtonY, ButtonWidth, ButtonHeight);
            Rectangle btnInitRect = new Rectangle(ButtonInitX, ButtonY, ButtonWidth, ButtonHeight);
            Rectangle btnRunRect = new Rectangle(ButtonRunX, ButtonY, ButtonWidth, ButtonHeight);

            // 自动运行按钮
            if (_isInitialized && Raylib.IsMouseButtonPressed(MouseButton.Left) && Raylib.CheckCollisionPointRec(mousePos, btnAutoRect))
            {
                if (_isAutoRunning)
                {
                    _isAutoStopRequested = true;
                }
                else
                {
                    if (!_isProcessing)
                    {
                        _isAutoRunning = true;
                        _isAutoStopRequested = false;
                    }
                }
            }

            // 初始化按钮
            if (!_isProcessing && !_isAutoRunning && Raylib.IsMouseButtonPressed(MouseButton.Left) && Raylib.CheckCollisionPointRec(mousePos, btnInitRect))
            {
                // 清空算法核心容器
                _priorityQueue.Clear();
                _visitedSet.Clear();

                // 重置最短路径相关状态
                _shortestPath.Clear();
                _isShortestPathCalculated = false;

                // 清空并重新初始化路径信息表
                _pathInfoTable.Clear();
                InitPathInfoTable(_mazeGrid);

                // 重新初始化A*起点
                InitAStar();

                // 清空视觉残留状态
                _displayTexts.Clear();
                _blinkNodes.Clear();

                // 重置按钮和算法状态
                _isInitialized = true;
                _isButtonClickable = true;
                _isProcessing = false;
                _currentProcessingCell = (0, 0);
            }

            // 运行按钮
            if (_isInitialized && !_isProcessing && !_isAutoRunning && _isButtonClickable && Raylib.IsMouseButtonPressed(MouseButton.Left) && Raylib.CheckCollisionPointRec(mousePos, btnRunRect))
            {
                StartProcessingHeapTop();
            }
        }

        // ===================== 绘制迷宫 =====================
        private static void DrawMazeGrid()
        {
            for (int row = 0; row < GridRows; row++)
            {
                for (int col = 0; col < GridCols; col++)
                {
                    Rectangle cellRect = new Rectangle(
                        col * CellSize,
                        row * CellSize,
                        CellSize,
                        CellSize
                    );

                    // 基础颜色
                    Color cellColor = GetCellColor(row, col);

                    // 闪烁效果
                    var blinkNode = _blinkNodes.FirstOrDefault(b => b.Cell == (row, col));
                    if (blinkNode.RemainTime > 0 && blinkNode.IsVisible)
                    {
                        cellColor = ColorBlink;
                    }

                    // 绘制单元格
                    Raylib.DrawRectangleRec(cellRect, cellColor);
                    Raylib.DrawRectangleLinesEx(cellRect, 1, Color.DarkGray);

                    // A*增强：在单元格中显示G值和H值（如果已访问）
                    if (_pathInfoTable.ContainsKey((row, col)) &&
                        _mazeGrid[row, col].State == MazeCellState.Path &&
                        _pathInfoTable[(row, col)].G_Distance < int.MaxValue)
                    {
                        var info = _pathInfoTable[(row, col)];
                        int h = ManhattanDistance((row, col));

                        // 显示G和H值
                        string gText = $"G:{info.G_Distance}";
                        string hText = $"H:{h}";

                        // 绘制G值（左上角）
                        Raylib.DrawText(
                            gText,
                            col * CellSize + 2,
                            row * CellSize + 2,
                            10,
                            Color.DarkBlue
                        );

                        // 绘制H值（右上角）
                        int hTextWidth = Raylib.MeasureText(hText, 10);
                        Raylib.DrawText(
                            hText,
                            col * CellSize + CellSize - hTextWidth - 2,
                            row * CellSize + 2,
                            10,
                            ColorHeuristic
                        );

                        // 在中心显示F值
                        if (!_visitedSet.Contains((row, col)))
                        {
                            string fText = $"F:{info.F_Score}";
                            int fTextWidth = Raylib.MeasureText(fText, 12);
                            Raylib.DrawText(
                                fText,
                                col * CellSize + (CellSize - fTextWidth) / 2,
                                row * CellSize + (CellSize - 12) / 2,
                                12,
                                Color.Red
                            );
                        }
                    }
                }
            }
        }

        // ===================== 绘制控制栏 =====================
        private static void DrawControlBar()
        {
            Raylib.DrawRectangle(0, MapHeight, WindowWidth, ControlBarHeight, new Color(240, 240, 240, 255));

            Vector2 mousePos = Raylib.GetMousePosition();
            int hoverRow = -1, hoverCol = -1;
            string coordText = "Current Cell: None";
            string pathText = "Path Info: None";
            string autoStatusText = _isAutoRunning
                ? (_isAutoStopRequested ? "Auto Run: STOPPING..." : "Auto Run: ON (Speed x2)")
                : "Auto Run: OFF";

            string algorithmInfo = "Algorithm: A* (终点出队即停止)";

            // 添加算法效率信息
            string efficiencyInfo = $"已访问: {_visitedSet.Count} 单元格, 队列: {_priorityQueue.Count}";

            string shortestPathText = _isShortestPathCalculated
                ? $"最短路径: 已找到 (长度: {(_shortestPath.Count > 0 ? _shortestPath.Count - 1 : 0)}步)"
                : "最短路径: 计算中...";

            if (mousePos.X >= 0 && mousePos.X < MapWidth && mousePos.Y >= 0 && mousePos.Y < MapHeight)
            {
                hoverCol = (int)(mousePos.X / CellSize);
                hoverRow = (int)(mousePos.Y / CellSize);
                hoverRow = Math.Clamp(hoverRow, 0, GridRows - 1);
                hoverCol = Math.Clamp(hoverCol, 0, GridCols - 1);
                coordText = $"当前单元格: 行 {hoverRow}, 列 {hoverCol}";

                if (_pathInfoTable.ContainsKey((hoverRow, hoverCol)))
                {
                    var pathInfo = _pathInfoTable[(hoverRow, hoverCol)];
                    string prevStr = (pathInfo.PrevRow == -1 && pathInfo.PrevCol == -1) ? "None" : $"({pathInfo.PrevRow}, {pathInfo.PrevCol})";
                    string gStr = pathInfo.G_Distance == int.MaxValue ? "∞" : pathInfo.G_Distance.ToString();
                    int h = ManhattanDistance((hoverRow, hoverCol));
                    string fStr = pathInfo.F_Score == int.MaxValue ? "∞" : pathInfo.F_Score.ToString();
                    pathText = $"路径信息: 前驱={prevStr}, G={gStr}, H={h}, F={fStr}";
                }
            }

            int textSize = 16;
            Raylib.DrawText(coordText, 10, 810, textSize, Color.Black);
            Raylib.DrawText(pathText, 10, 840, textSize, Color.Black);
            Raylib.DrawText(algorithmInfo, 300, 810, textSize, Color.DarkBlue);
            Raylib.DrawText(efficiencyInfo, 300, 840, textSize, Color.DarkGreen);
            Raylib.DrawText(shortestPathText, 550, 810, textSize, _isShortestPathCalculated ? Color.Purple : Color.Black);
            Raylib.DrawText(autoStatusText, 550, 840, textSize, _isAutoRunning ? Color.Orange : Color.Black);

            // 如果终点已访问，显示特殊提示
            if (_visitedSet.Contains(_endCell))
            {
                Raylib.DrawText("✓ 终点已找到，算法已停止", 10, 870, 18, Color.Green);
            }
        }

        // ===================== 按钮绘制 =====================
        private static void DrawButton(Rectangle rect, string text, bool enabled)
        {
            if (_isAutoRunning && (rect.X == ButtonInitX || rect.X == ButtonRunX))
            {
                enabled = false;
            }

            Color bgColor;
            if (rect.X == ButtonAutoX)
            {
                if (!enabled)
                {
                    bgColor = Color.DarkGray;
                }
                else if (_isAutoRunning)
                {
                    bgColor = Raylib.CheckCollisionPointRec(Raylib.GetMousePosition(), rect) ? new Color(180, 180, 180, 255) : Color.Gray;
                }
                else
                {
                    bgColor = Raylib.CheckCollisionPointRec(Raylib.GetMousePosition(), rect) ? Color.LightGray : Color.White;
                }
            }
            else
            {
                bgColor = enabled
                    ? (Raylib.CheckCollisionPointRec(Raylib.GetMousePosition(), rect) ? Color.Gray : Color.LightGray)
                    : Color.DarkGray;
            }

            Color textColor = enabled ? Color.Black : Color.Gray;

            Raylib.DrawRectangleRec(rect, bgColor);
            Raylib.DrawRectangleLinesEx(rect, 2, Color.DarkGray);
            int textWidth = Raylib.MeasureText(text, 16);
            Raylib.DrawText(
                text,
                (int)(rect.X + (rect.Width - textWidth) / 2),
                (int)(rect.Y + (rect.Height - 16) / 2),
                16,
                textColor
            );
        }

        // ===================== 辅助函数：计时器更新 =====================
        private static void UpdateTimers(float deltaTime)
        {
            for (int i = _displayTexts.Count - 1; i >= 0; i--)
            {
                var text = _displayTexts[i];
                text.RemainTime -= deltaTime;
                if (text.RemainTime <= 0)
                {
                    _displayTexts.RemoveAt(i);
                }
                else
                {
                    _displayTexts[i] = text;
                }
            }

            for (int i = _blinkNodes.Count - 1; i >= 0; i--)
            {
                var blink = _blinkNodes[i];
                blink.RemainTime -= deltaTime;

                if ((float)Raylib.GetTime() - blink.LastBlinkTime >= blink.BlinkInterval)
                {
                    blink.IsVisible = !blink.IsVisible;
                    blink.LastBlinkTime = (float)Raylib.GetTime();
                }

                if (blink.RemainTime <= 0)
                {
                    _blinkNodes.RemoveAt(i);
                }
                else
                {
                    _blinkNodes[i] = blink;
                }
            }
        }

        // ===================== 辅助函数：添加显示文本 =====================
        private static void AddDisplayText(string text, (int row, int col) cell)
        {
            _displayTexts.Add(new DisplayText
            {
                Text = text,
                Position = new Vector2(
                    cell.col * CellSize + CellSize / 2,
                    cell.row * CellSize + CellSize / 2
                ),
                RemainTime = 1.0f
            });
        }

        // ===================== 辅助函数：添加闪烁节点 =====================
        private static void AddBlinkNode((int row, int col) cell)
        {
            _blinkNodes.Add(new BlinkNode
            {
                Cell = cell,
                RemainTime = 1.0f,
                BlinkInterval = 0.2f,
                LastBlinkTime = (float)Raylib.GetTime(),
                IsVisible = true
            });
        }

        // ===================== 辅助函数：绘制显示文本 =====================
        private static void DrawDisplayTexts()
        {
            foreach (var text in _displayTexts)
            {
                if (text.RemainTime > 0)
                {
                    int textWidth = Raylib.MeasureText(text.Text, 12);
                    Raylib.DrawText(
                        text.Text,
                        (int)(text.Position.X - textWidth / 2),
                        (int)(text.Position.Y - 6),
                        12,
                        Color.Black
                    );
                }
            }
        }

        // ===================== 辅助函数：判断邻接 =====================
        private static bool IsAdjacent((int row, int col) a, (int row, int col) b)
        {
            return (a.row == b.row && Math.Abs(a.col - b.col) == 1) ||
                   (a.col == b.col && Math.Abs(a.row - b.row) == 1);
        }

        // ===================== 辅助函数：获取有效邻接节点 =====================
        private static List<(int row, int col)> GetValidAdjacentCells((int row, int col) cell)
        {
            List<(int row, int col)> adjCells = new List<(int row, int col)>();
            var directions = new List<(int dr, int dc)> { (-1, 0), (1, 0), (0, -1), (0, 1) };

            foreach (var dir in directions)
            {
                int newRow = cell.row + dir.dr;
                int newCol = cell.col + dir.dc;

                if (newRow >= 0 && newRow < GridRows && newCol >= 0 && newCol < GridCols &&
                    _mazeGrid[newRow, newCol].State == MazeCellState.Path &&
                    !_visitedSet.Contains((newRow, newCol)))
                {
                    adjCells.Add((newRow, newCol));
                }
            }

            return adjCells;
        }

        // ===================== 生成随机迷宫 =====================
        private static void GenerateSimpleRandomMaze(MazeCell[,] mazeGrid)
        {
            Random random = new Random();
            for (int row = 0; row < GridRows; row++)
            {
                for (int col = 0; col < GridCols; col++)
                {
                    bool isWall = random.Next(10) < 3;
                    mazeGrid[row, col] = new MazeCell { State = isWall ? MazeCellState.Wall : MazeCellState.Path };
                }
            }

            // 强制中心区域为路
            int centerRow = GridRows / 2;
            int centerCol = GridCols / 2;
            mazeGrid[centerRow, centerCol].State = MazeCellState.Path;
            mazeGrid[centerRow + 1, centerCol].State = MazeCellState.Path;
            mazeGrid[centerRow, centerCol + 1].State = MazeCellState.Path;
            mazeGrid[centerRow - 1, centerCol].State = MazeCellState.Path;
            mazeGrid[centerRow, centerCol - 1].State = MazeCellState.Path;
        }

        // ===================== 找第一个空白格 =====================
        private static Vector2 FindFirstEmptyCell(MazeCell[,] mazeGrid)
        {
            for (int row = 0; row < GridRows; row++)
            {
                for (int col = 0; col < GridCols; col++)
                {
                    if (mazeGrid[row, col].State == MazeCellState.Path)
                    {
                        return new Vector2(
                            col * CellSize + CellSize / 2,
                            row * CellSize + CellSize / 2
                        );
                    }
                }
            }
            return new Vector2(MapWidth / 2, MapHeight / 2);
        }

        // ===================== 找最后一个空白格 =====================
        private static Vector2 FindLastEmptyCell(MazeCell[,] mazeGrid)
        {
            for (int row = GridRows - 1; row >= 0; row--)
            {
                for (int col = GridCols - 1; col >= 0; col--)
                {
                    if (mazeGrid[row, col].State == MazeCellState.Path)
                    {
                        return new Vector2(
                            col * CellSize + CellSize / 2,
                            row * CellSize + CellSize / 2
                        );
                    }
                }
            }
            return new Vector2(MapWidth / 2, MapHeight / 2);
        }

        // ===================== 初始化路径信息表 =====================
        private static void InitPathInfoTable(MazeCell[,] mazeGrid)
        {
            _pathInfoTable = new Dictionary<(int, int), PathInfo>();
            for (int row = 0; row < GridRows; row++)
            {
                for (int col = 0; col < GridCols; col++)
                {
                    if (mazeGrid[row, col].State == MazeCellState.Path)
                    {
                        int h = ManhattanDistance((row, col));
                        _pathInfoTable[(row, col)] = new PathInfo
                        {
                            PrevRow = -1,
                            PrevCol = -1,
                            G_Distance = int.MaxValue,
                            F_Score = int.MaxValue
                        };
                    }
                }
            }
        }

        // ===================== 初始化A*起点 =====================
        private static void InitAStar()
        {
            // 重置起点的路径信息
            int startH = ManhattanDistance(_startCell);
            int startF = CalculateFScore(0, _startCell);

            if (_pathInfoTable.ContainsKey(_startCell))
            {
                _pathInfoTable[_startCell] = new PathInfo
                {
                    PrevRow = -1,
                    PrevCol = -1,
                    G_Distance = 0,
                    F_Score = startF
                };
            }
            else
            {
                _pathInfoTable.Add(_startCell, new PathInfo
                {
                    PrevRow = -1,
                    PrevCol = -1,
                    G_Distance = 0,
                    F_Score = startF
                });
            }

            // A*核心修改：入队时使用F值作为优先级
            _priorityQueue.Enqueue(_startCell, startF);

            // 重置算法运行的临时状态
            _currentProcessingCell = (0, 0);
            _currentAdjacentCells.Clear();
            _currentAdjIndex = 0;
            _animationTimer = 0.0f;
        }
    }
}