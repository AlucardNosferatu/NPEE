using Raylib_cs;
using System.Numerics;

namespace DijkstraMapVisualization
{
    // 网格单元格类型
    public enum CellType
    {
        Empty,
        Target,
        Obstacle
    }

    // 网格单元格
    public class GridCell
    {
        public CellType Type { get; set; }
        public int Distance { get; set; }
        public bool Visited { get; set; }
        public bool Processed { get; set; }

        public GridCell()
        {
            Type = CellType.Empty;
            Distance = int.MaxValue;
            Visited = false;
            Processed = false;
        }
    }

    public class DijkstraMap
    {
        // 网格参数
        private const int GridWidth = 20;
        private const int GridHeight = 15;
        private const int CellSize = 40;
        private const int Margin = 10;

        // UI参数
        private const int ButtonHeight = 40;
        private const int WindowWidth = GridWidth * CellSize + 2 * Margin;
        private const int WindowHeight = GridHeight * CellSize + 2 * Margin + ButtonHeight * 2 + 40;

        // 网格数据
        private GridCell[,] grid;
        private List<Vector2> targetCells;
        private Queue<Vector2> cellsToProcess;

        // 算法状态
        private bool isRunning = false;
        private bool isPaused = true;
        private bool isCompleted = false;
        private int currentStep = 0;
        private float stepTimer = 0f;
        private const float StepDelay = 0.5f; // 每步延迟（秒）

        // UI按钮区域
        private Rectangle resetButton;
        private Rectangle startButton;
        private Rectangle pauseButton;
        private Rectangle stepButton;
        private Rectangle clearButton;

        // 颜色定义
        private Color emptyColor = new Color(240, 240, 240, 255);
        private Color targetColor = new Color(0, 200, 0, 255);
        private Color obstacleColor = new Color(80, 80, 80, 255);
        private Color processedColor = new Color(200, 230, 255, 255);
        private Color visitedColor = new Color(230, 240, 255, 255);
        private Color textColor = new Color(20, 20, 20, 255);
        private Color buttonColor = new Color(70, 130, 180, 255);
        private Color buttonHoverColor = new Color(100, 160, 210, 255);

        // 方向数组（上、右、下、左）
        private Vector2[] directions = new Vector2[]
        {
            new Vector2(0, -1),  // 上
            new Vector2(1, 0),   // 右
            new Vector2(0, 1),   // 下
            new Vector2(-1, 0)   // 左
        };

        public DijkstraMap()
        {
            grid = new GridCell[GridWidth, GridHeight];
            targetCells = new List<Vector2>();
            cellsToProcess = new Queue<Vector2>();

            // 初始化网格
            for (int x = 0; x < GridWidth; x++)
            {
                for (int y = 0; y < GridHeight; y++)
                {
                    grid[x, y] = new GridCell();
                }
            }

            // 设置初始目标点
            SetTarget(3, 3);
            SetTarget(15, 10);

            // 设置一些初始障碍物
            SetObstacle(5, 5);
            SetObstacle(5, 6);
            SetObstacle(6, 5);
            SetObstacle(6, 6);
            SetObstacle(10, 7);
            SetObstacle(10, 8);
            SetObstacle(10, 9);
            SetObstacle(11, 8);

            // 初始化按钮
            int buttonWidth = 120;
            int buttonSpacing = 10;
            int startX = Margin + 20;
            int buttonY = GridHeight * CellSize + Margin + 10;

            startButton = new Rectangle(startX, buttonY, buttonWidth, ButtonHeight);
            pauseButton = new Rectangle(startX + buttonWidth + buttonSpacing, buttonY, buttonWidth, ButtonHeight);
            stepButton = new Rectangle(startX + 2 * (buttonWidth + buttonSpacing), buttonY, buttonWidth, ButtonHeight);

            int secondRowY = buttonY + ButtonHeight + 5;
            resetButton = new Rectangle(startX, secondRowY, buttonWidth, ButtonHeight);
            clearButton = new Rectangle(startX + buttonWidth + buttonSpacing, secondRowY, buttonWidth, ButtonHeight);

            // 初始化算法
            InitializeAlgorithm();
        }

        private void SetTarget(int x, int y)
        {
            if (IsInBounds(x, y) && grid[x, y].Type != CellType.Obstacle)
            {
                grid[x, y].Type = CellType.Target;
                grid[x, y].Distance = 0;
                targetCells.Add(new Vector2(x, y));
            }
        }

        private void SetObstacle(int x, int y)
        {
            if (IsInBounds(x, y) && grid[x, y].Type != CellType.Target)
            {
                grid[x, y].Type = CellType.Obstacle;
            }
        }

        private bool IsInBounds(int x, int y)
        {
            return x >= 0 && x < GridWidth && y >= 0 && y < GridHeight;
        }

        private void InitializeAlgorithm()
        {
            // 重置所有单元格的状态
            for (int x = 0; x < GridWidth; x++)
            {
                for (int y = 0; y < GridHeight; y++)
                {
                    var cell = grid[x, y];

                    if (cell.Type == CellType.Target)
                    {
                        cell.Distance = 0;
                        cell.Visited = true;
                        cell.Processed = false;
                    }
                    else if (cell.Type == CellType.Obstacle)
                    {
                        cell.Distance = int.MaxValue;
                        cell.Visited = false;
                        cell.Processed = true; // 障碍物视为已处理
                    }
                    else
                    {
                        cell.Distance = int.MaxValue;
                        cell.Visited = false;
                        cell.Processed = false;
                    }
                }
            }

            // 清空处理队列并添加所有目标点
            cellsToProcess.Clear();
            foreach (var target in targetCells)
            {
                cellsToProcess.Enqueue(target);
            }

            currentStep = 0;
            isCompleted = false;
            isRunning = false;
            isPaused = true;
        }

        private void RunAlgorithmStep()
        {
            if (isCompleted || cellsToProcess.Count == 0)
            {
                isCompleted = true;
                isRunning = false;
                return;
            }

            // 处理当前队列中的所有单元格（这一层的所有单元格）
            int cellsThisLevel = cellsToProcess.Count;

            for (int i = 0; i < cellsThisLevel; i++)
            {
                Vector2 current = cellsToProcess.Dequeue();
                int x = (int)current.X;
                int y = (int)current.Y;

                grid[x, y].Processed = true;

                // 检查四个方向的邻居
                foreach (var dir in directions)
                {
                    int nx = x + (int)dir.X;
                    int ny = y + (int)dir.Y;

                    if (IsInBounds(nx, ny) && grid[nx, ny].Type != CellType.Obstacle)
                    {
                        var neighbor = grid[nx, ny];

                        // 如果找到更短的路径，更新邻居的距离
                        int newDistance = grid[x, y].Distance + 1;
                        if (newDistance < neighbor.Distance)
                        {
                            neighbor.Distance = newDistance;

                            // 如果邻居还未被访问，将其加入队列
                            if (!neighbor.Visited)
                            {
                                neighbor.Visited = true;
                                cellsToProcess.Enqueue(new Vector2(nx, ny));
                            }
                        }
                    }
                }
            }

            currentStep++;

            // 检查是否完成
            if (cellsToProcess.Count == 0)
            {
                isCompleted = true;
                isRunning = false;
            }
        }

        private void HandleInput()
        {
            // 鼠标位置
            Vector2 mousePos = Raylib.GetMousePosition();

            // 检查是否点击了网格单元格
            if (Raylib.IsMouseButtonPressed(MouseButton.Left))
            {
                // 检查是否点击了按钮
                if (Raylib.CheckCollisionPointRec(mousePos, startButton))
                {
                    if (!isCompleted)
                    {
                        isRunning = true;
                        isPaused = false;
                    }
                }
                else if (Raylib.CheckCollisionPointRec(mousePos, pauseButton))
                {
                    isRunning = false;
                    isPaused = true;
                }
                else if (Raylib.CheckCollisionPointRec(mousePos, stepButton))
                {
                    if (!isCompleted)
                    {
                        RunAlgorithmStep();
                        isRunning = false;
                        isPaused = true;
                    }
                }
                else if (Raylib.CheckCollisionPointRec(mousePos, resetButton))
                {
                    InitializeAlgorithm();
                }
                else if (Raylib.CheckCollisionPointRec(mousePos, clearButton))
                {
                    // 清除所有目标点和障碍物
                    for (int x = 0; x < GridWidth; x++)
                    {
                        for (int y = 0; y < GridHeight; y++)
                        {
                            grid[x, y].Type = CellType.Empty;
                        }
                    }
                    targetCells.Clear();
                    InitializeAlgorithm();
                }
                else
                {
                    // 检查是否点击了网格单元格
                    int gridX = (int)((mousePos.X - Margin) / CellSize);
                    int gridY = (int)((mousePos.Y - Margin) / CellSize);

                    if (gridX >= 0 && gridX < GridWidth && gridY >= 0 && gridY < GridHeight)
                    {
                        // 切换单元格类型（普通<->目标<->障碍物）
                        var cell = grid[gridX, gridY];

                        if (cell.Type == CellType.Empty)
                        {
                            // 设置为目标
                            cell.Type = CellType.Target;
                            cell.Distance = 0;
                            targetCells.Add(new Vector2(gridX, gridY));
                        }
                        else if (cell.Type == CellType.Target)
                        {
                            // 设置为障碍物
                            cell.Type = CellType.Obstacle;
                            targetCells.Remove(new Vector2(gridX, gridY));
                        }
                        else if (cell.Type == CellType.Obstacle)
                        {
                            // 设置为普通
                            cell.Type = CellType.Empty;
                        }

                        // 重新初始化算法
                        InitializeAlgorithm();
                    }
                }
            }

            // 右键设置障碍物
            if (Raylib.IsMouseButtonPressed(MouseButton.Right))
            {
                int gridX = (int)((mousePos.X - Margin) / CellSize);
                int gridY = (int)((mousePos.Y - Margin) / CellSize);

                if (gridX >= 0 && gridX < GridWidth && gridY >= 0 && gridY < GridHeight)
                {
                    var cell = grid[gridX, gridY];

                    if (cell.Type == CellType.Empty)
                    {
                        cell.Type = CellType.Obstacle;
                        if (targetCells.Contains(new Vector2(gridX, gridY)))
                        {
                            targetCells.Remove(new Vector2(gridX, gridY));
                        }
                    }
                    else if (cell.Type == CellType.Obstacle)
                    {
                        cell.Type = CellType.Empty;
                    }

                    InitializeAlgorithm();
                }
            }
        }

        private void Update()
        {
            if (isRunning && !isPaused)
            {
                stepTimer += Raylib.GetFrameTime();

                if (stepTimer >= StepDelay)
                {
                    RunAlgorithmStep();
                    stepTimer = 0f;
                }
            }
        }

        private void DrawGrid()
        {
            for (int x = 0; x < GridWidth; x++)
            {
                for (int y = 0; y < GridHeight; y++)
                {
                    var cell = grid[x, y];
                    int screenX = Margin + x * CellSize;
                    int screenY = Margin + y * CellSize;

                    // 确定单元格颜色
                    Color cellColor = emptyColor;

                    if (cell.Type == CellType.Target)
                    {
                        cellColor = targetColor;
                    }
                    else if (cell.Type == CellType.Obstacle)
                    {
                        cellColor = obstacleColor;
                    }
                    else if (cell.Processed)
                    {
                        // 根据距离值设置颜色渐变（距离越小颜色越深）
                        if (cell.Distance < int.MaxValue)
                        {
                            int intensity = 255 - Math.Min(cell.Distance * 20, 200);
                            cellColor = new Color(200 - intensity / 2, 230 - intensity / 2, 255, 255);
                        }
                        else
                        {
                            cellColor = emptyColor;
                        }
                    }
                    else if (cell.Visited)
                    {
                        cellColor = visitedColor;
                    }

                    // 绘制单元格背景
                    Raylib.DrawRectangle(screenX, screenY, CellSize, CellSize, cellColor);

                    // 绘制单元格边框
                    Raylib.DrawRectangleLines(screenX, screenY, CellSize, CellSize, Color.DarkGray);

                    // 在非障碍物单元格中显示距离
                    if (cell.Type != CellType.Obstacle && cell.Distance < int.MaxValue)
                    {
                        string distanceText = cell.Distance.ToString();
                        int fontSize = 16;
                        int textWidth = Raylib.MeasureText(distanceText, fontSize);
                        Raylib.DrawText(
                            distanceText,
                            screenX + CellSize / 2 - textWidth / 2,
                            screenY + CellSize / 2 - fontSize / 2,
                            fontSize,
                            textColor
                        );
                    }
                }
            }
        }

        private void DrawUI()
        {
            // 绘制按钮
            DrawButton(startButton, "Continue", isRunning && !isPaused);
            DrawButton(pauseButton, "Pause", isPaused && isRunning);
            DrawButton(stepButton, "Step", false);
            DrawButton(resetButton, "Reset", false);
            DrawButton(clearButton, "Clear", false);

            // 绘制说明文本
            int infoY = GridHeight * CellSize + Margin + 2 * ButtonHeight + 20;
            Raylib.DrawText("Left-click on a cell: Switch type (Normal->Target->Obstacle->Normal)", Margin + 20, infoY, 18, Color.DarkGray);
            Raylib.DrawText("Right-click on the cell: toggle obstacle status", Margin + 20, infoY + 25, 18, Color.DarkGray);

            // 绘制状态信息
            string statusText = isCompleted ? "The algorithm has been completed!" :
                               isRunning ? "The algorithm is running .." :
                               isPaused ? "Algorithm paused" : "Ready";
            Color statusColor = isCompleted ? Color.Green :
                               isRunning ? Color.Blue :
                               Color.DarkGray;

            Raylib.DrawText($"Status: {statusText}", WindowWidth - 250, Margin, 20, statusColor);
            Raylib.DrawText($"Current Step: {currentStep}", WindowWidth - 250, Margin + 30, 20, Color.DarkGray);

            // 绘制图例
            int legendY = infoY + 60;
            DrawLegendItem(Margin + 20, legendY, targetColor, "Target (dist=0)");
            DrawLegendItem(Margin + 200, legendY, obstacleColor, "Obstacle (impassable)");
            DrawLegendItem(Margin + 400, legendY, visitedColor, "Visited but not processed");
            DrawLegendItem(Margin + 600, legendY, new Color(150, 190, 255, 255), "Processed (The darker the color, the closer the distance)");
        }

        private void DrawButton(Rectangle rect, string text, bool isActive)
        {
            Vector2 mousePos = Raylib.GetMousePosition();
            bool isHoveRed = Raylib.CheckCollisionPointRec(mousePos, rect);

            Color buttonColor = isActive ? Color.Green :
                               isHoveRed ? buttonHoverColor : this.buttonColor;

            Raylib.DrawRectangleRec(rect, buttonColor);
            Raylib.DrawRectangleLines((int)rect.X, (int)rect.Y, (int)rect.Width, (int)rect.Height, Color.DarkGray);

            int textWidth = Raylib.MeasureText(text, 20);
            Raylib.DrawText(
                text,
                (int)(rect.X + rect.Width / 2 - textWidth / 2),
                (int)(rect.Y + rect.Height / 2 - 10),
                20,
                Color.White
            );
        }

        private void DrawLegendItem(int x, int y, Color color, string text)
        {
            Raylib.DrawRectangle(x, y, 20, 20, color);
            Raylib.DrawRectangleLines(x, y, 20, 20, Color.DarkGray);
            Raylib.DrawText(text, x + 30, y, 18, Color.DarkGray);
        }

        public void Run()
        {
            Raylib.InitWindow(WindowWidth, WindowHeight, "Dijkstra Map Visualizer");
            Raylib.SetTargetFPS(60);

            while (!Raylib.WindowShouldClose())
            {
                HandleInput();
                Update();

                Raylib.BeginDrawing();
                Raylib.ClearBackground(Color.RayWhite);

                DrawGrid();
                DrawUI();

                Raylib.EndDrawing();
            }

            Raylib.CloseWindow();
        }
    }

    internal class Program
    {
        public static void Main()
        {
            DijkstraMap dijkstraMap = new DijkstraMap();
            dijkstraMap.Run();
        }
    }
}