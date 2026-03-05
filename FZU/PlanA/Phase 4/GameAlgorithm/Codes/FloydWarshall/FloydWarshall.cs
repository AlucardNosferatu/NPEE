// FloydWarshall.cs
using Raylib_cs;
using System.Numerics;

public class FloydWarshallVisualization
{
    // ==================== UI配置常量 ====================
    private const int SCREEN_WIDTH = 1200;
    private const int SCREEN_HEIGHT = 800;

    // 布局常量
    private const int PADDING = 30;
    private const int TITLE_Y = 10;
    private const int INSTRUCTIONS_Y = TITLE_Y + PADDING;
    private const int TOP_BAR_HEIGHT = INSTRUCTIONS_Y + PADDING - 5;

    // 图形区域
    private const int GRAPH_AREA_X = PADDING;
    private const int GRAPH_AREA_Y = TOP_BAR_HEIGHT + PADDING + BUTTON_HEIGHT + 5;
    private const int GRAPH_AREA_WIDTH = 500;
    private const int GRAPH_AREA_HEIGHT = 500;

    // 矩阵区域
    private const int MATRIX_AREA_X = GRAPH_AREA_X + GRAPH_AREA_WIDTH + PADDING;
    private const int MATRIX_AREA_Y = GRAPH_AREA_Y;
    private const int MATRIX_AREA_WIDTH = 500;
    private const int MATRIX_AREA_HEIGHT = GRAPH_AREA_HEIGHT;

    // 按钮配置
    private const int BUTTON_Y = TOP_BAR_HEIGHT;
    private const int BUTTON_WIDTH = 200;
    private const int BUTTON_HEIGHT = 25;
    private const int BUTTON_SPACING = 10;

    // 图例区域
    private const int LEGEND_X = MATRIX_AREA_X;
    private const int LEGEND_Y = MATRIX_AREA_Y + MATRIX_AREA_HEIGHT + 20;

    // 状态区域
    private const int STATUS_X = GRAPH_AREA_X;
    private const int STATUS_Y = GRAPH_AREA_Y + GRAPH_AREA_HEIGHT + 20;

    // 文本大小
    private const int TITLE_FONT_SIZE = 30;
    private const int SUBTITLE_FONT_SIZE = 24;
    private const int TEXT_FONT_SIZE = 20;
    private const int SMALL_TEXT_FONT_SIZE = 16;
    private const int BUTTON_FONT_SIZE = 20;

    // ==================== 自动步进配置 ====================
    private const float STEP_WAIT = 0.25f; // 自动步进间隔时间（秒）
    private float stepTimer = 0f; // 自动步进计时器
    private bool autoStepping = false; // 是否正在自动步进

    // ==================== 字符串常量 ====================
    private const string WINDOW_TITLE = "Floyd-Warshall Algorithm Visualizer";
    private const string TITLE = "Floyd-Warshall Algorithm Visualizer";
    private const string INSTRUCTIONS = "Instructions: Click buttons to control execution, Space: Step, R: Reset, M: Toggle Matrix";

    // 按钮文本
    private const string BTN_START = "Start/Pause";
    private const string BTN_PAUSE = "Pause";
    private const string BTN_STEP = "Step";
    private const string BTN_RESET = "Reset";
    private const string BTN_TOGGLE_MATRIX = "Toggle Matrix";
    private const string BTN_TOGGLE_PATHS = "Toggle Paths";
    private const string BTN_SHOW_DIST = "Show Distance";
    private const string BTN_SHOW_PATH = "Show Path";
    private const string BTN_HIDE_PATH = "Hide Path";

    // 标题文本
    private const string GRAPH_TITLE = "Graph Visualization";
    private const string MATRIX_TITLE_DIST = "Distance Matrix (D)";
    private const string MATRIX_TITLE_PATH = "Path Matrix (P)";
    private const string LEGEND_TITLE = "Legend:";
    private const string NODE_LABEL = "Nodes:";
    private const string PROCESSING_LABEL = "Current Processing:";

    // 图例项
    private const string LEGEND_K = "* Intermediate node K";
    private const string LEGEND_I = "* Starting node I";
    private const string LEGEND_J = "* Destination node J";
    private const string LEGEND_CELL = "* Current cell";

    // 状态文本
    private const string STATUS_IDLE = "Click 'Start/Pause' to begin";
    private const string STATUS_PROCESSING_K = "Current Step: Select intermediate node K = V{0}";
    private const string STATUS_PROCESSING_I = "Current Step: Select starting node I = V{0}";
    private const string STATUS_PROCESSING_J_DIRECT = "Check: D[{0},{1}] = {2}";
    private const string STATUS_PROCESSING_J_COMPARE = "Check: D[{0},{1}] > D[{0},{2}] + D[{2},{1}] ? {3} > {4} + {5} = {6} ?";
    private const string STATUS_UPDATING = "Update: D[{0},{1}] = {2} + {3} = {4}";
    private const string STATUS_COMPLETED = "Algorithm completed! All shortest paths calculated";
    private const string STATUS_SHORTEST_PATHS = "Shortest Path Examples:";
    private const string STATUS_PATH_FORMAT = "V{0}->V{1}: {2} (Distance={3})";
    private const string STATUS_UNREACHABLE = "Unreachable";

    // ==================== 算法状态枚举 ====================
    private enum AlgorithmState
    {
        Idle,
        ProcessingK,
        ProcessingI,
        ProcessingJ,
        Updating,
        Completed
    }

    // ==================== 图的相关数据 ====================
    private int[,] graph;
    private int[,] dist;
    private int[,] next;
    private int nodeCount = 5;

    // ==================== 算法控制变量 ====================
    private AlgorithmState state = AlgorithmState.Idle;
    private int currentK = -1;
    private int currentI = -1;
    private int currentJ = -1;
    private bool isPaused = true;
    private bool showDistances = true;
    private bool showPaths = false;

    // ==================== 动画控制 ====================
    private float animationTimer = 0f;
    private const float ANIMATION_DURATION = 0.5f;
    private bool isAnimating = false;

    // ==================== 颜色定义 ====================
    private Color[] nodeColors = {
        Color.Red, Color.Green, Color.Blue,
        Color.Orange, Color.Purple,
        Color.Pink, Color.Yellow,
        Color.SkyBlue, Color.Lime, Color.Violet
    };

    // ==================== UI布局对象 ====================
    private Rectangle graphArea;
    private Rectangle matrixArea;
    private Vector2[] nodePositions;
    private Button[] buttons;

    // ==================== Button类定义 ====================
    public class Button
    {
        public Rectangle Bounds;
        public string Text;
        public Color Color;
        public Color TextColor;
        public Action OnClick;

        public Button(Rectangle bounds, string text, Color color, Action onClick)
        {
            Bounds = bounds;
            Text = text;
            Color = color;
            TextColor = Color.White;
            OnClick = onClick;
        }

        public void Draw()
        {
            Raylib.DrawRectangleRec(Bounds, Color);
            Raylib.DrawRectangleLinesEx(Bounds, 2, Color.Black);

            int fontSize = BUTTON_FONT_SIZE;
            Vector2 textSize = Raylib.MeasureTextEx(Raylib.GetFontDefault(), Text, fontSize, 1);
            Vector2 textPos = new Vector2(
                Bounds.X + Bounds.Width / 2 - textSize.X / 2,
                Bounds.Y + Bounds.Height / 2 - textSize.Y / 2
            );
            Raylib.DrawText(Text, (int)textPos.X, (int)textPos.Y, fontSize, TextColor);
        }

        public bool IsClicked()
        {
            if (Raylib.IsMouseButtonPressed(MouseButton.Left))
            {
                Vector2 mousePos = Raylib.GetMousePosition();
                return Raylib.CheckCollisionPointRec(mousePos, Bounds);
            }
            return false;
        }
    }

    // ==================== 主程序入口 ====================
    public static void Main()
    {
        FloydWarshallVisualization demo = new FloydWarshallVisualization();
        demo.Initialize();
        demo.Run();
    }

    // ==================== 初始化方法 ====================
    private void Initialize()
    {
        // 初始化窗口
        Raylib.InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE);
        Raylib.SetTargetFPS(60);

        // 初始化布局对象
        graphArea = new Rectangle(GRAPH_AREA_X, GRAPH_AREA_Y, GRAPH_AREA_WIDTH, GRAPH_AREA_HEIGHT);
        matrixArea = new Rectangle(MATRIX_AREA_X, MATRIX_AREA_Y, MATRIX_AREA_WIDTH, MATRIX_AREA_HEIGHT);

        // 初始化示例图
        InitializeExampleGraph();

        // 初始化节点位置
        nodePositions = new Vector2[nodeCount];
        float centerX = graphArea.X + graphArea.Width / 2;
        float centerY = graphArea.Y + graphArea.Height / 2;
        float radius = Math.Min(graphArea.Width, graphArea.Height) * 0.4f;

        for (int i = 0; i < nodeCount; i++)
        {
            float angle = (float)(2 * Math.PI * i / nodeCount);
            nodePositions[i] = new Vector2(
                centerX + radius * (float)Math.Cos(angle),
                centerY + radius * (float)Math.Sin(angle)
            );
        }

        // 初始化按钮
        InitializeButtons();

        // 初始化矩阵
        InitializeMatrices();
    }

    private void InitializeExampleGraph()
    {
        const int INF = 99999;

        graph = new int[,] {
            {0, 3, INF, 5, INF},
            {2, 0, INF, 4, INF},
            {INF, 1, 0, INF, INF},
            {INF, INF, 2, 0, INF},
            {INF, INF, INF, 1, 0}
        };
    }

    private void InitializeMatrices()
    {
        dist = new int[nodeCount, nodeCount];
        next = new int[nodeCount, nodeCount];

        for (int i = 0; i < nodeCount; i++)
        {
            for (int j = 0; j < nodeCount; j++)
            {
                dist[i, j] = graph[i, j];
                if (i != j && graph[i, j] < 99999)
                    next[i, j] = j;
                else
                    next[i, j] = -1;
            }
        }
    }

    private void InitializeButtons()
    {
        int buttonX = PADDING;
        buttons = new Button[]
        {
            new Button(new Rectangle(buttonX, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT),
                      BTN_START, Color.Green, StartAlgorithm),
            new Button(new Rectangle(buttonX += BUTTON_WIDTH + BUTTON_SPACING, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT),
                      BTN_STEP, Color.Blue, StepAlgorithm),
            new Button(new Rectangle(buttonX += BUTTON_WIDTH + BUTTON_SPACING, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT),
                      BTN_RESET, Color.Orange, ResetAlgorithm),
            new Button(new Rectangle(buttonX += BUTTON_WIDTH + BUTTON_SPACING, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT),
                      BTN_TOGGLE_MATRIX, Color.Purple, ToggleMatrix),
            new Button(new Rectangle(buttonX += BUTTON_WIDTH + BUTTON_SPACING, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT),
                      BTN_TOGGLE_PATHS, Color.SkyBlue, TogglePaths)
        };
    }

    // ==================== 主循环 ====================
    private void Run()
    {
        while (!Raylib.WindowShouldClose())
        {
            ProcessInput();
            Update();
            Draw();
        }

        Raylib.CloseWindow();
    }

    // ==================== 输入处理 ====================
    private void ProcessInput()
    {
        foreach (var button in buttons)
        {
            if (button.IsClicked())
                button.OnClick();
        }

        if (Raylib.IsKeyPressed(KeyboardKey.Space))
            StepAlgorithm();
        if (Raylib.IsKeyPressed(KeyboardKey.R))
            ResetAlgorithm();
        if (Raylib.IsKeyPressed(KeyboardKey.M))
            ToggleMatrix();
    }

    // ==================== 更新逻辑 ====================
    private void Update()
    {
        // 更新动画计时器
        if (isAnimating)
        {
            animationTimer += Raylib.GetFrameTime();
            if (animationTimer >= ANIMATION_DURATION)
            {
                animationTimer = 0;
                isAnimating = false;

                // 如果状态是Completed，停止所有动画
                if (state == AlgorithmState.Completed)
                {
                    isAnimating = false;
                    autoStepping = false;
                }
            }
        }

        // 自动步进逻辑
        if (autoStepping && !isAnimating && state != AlgorithmState.Completed)
        {
            stepTimer += Raylib.GetFrameTime();
            if (stepTimer >= STEP_WAIT)
            {
                stepTimer = 0;
                ExecuteNextStep();
            }
        }
    }

    private void ExecuteNextStep()
    {
        switch (state)
        {
            case AlgorithmState.Idle:
                currentK = 0;
                currentI = 0;
                currentJ = 0;
                state = AlgorithmState.ProcessingK;
                isAnimating = true;
                break;

            case AlgorithmState.ProcessingK:
                state = AlgorithmState.ProcessingI;
                isAnimating = true;
                break;

            case AlgorithmState.ProcessingI:
                state = AlgorithmState.ProcessingJ;
                isAnimating = true;
                break;

            case AlgorithmState.ProcessingJ:
                int oldDist = dist[currentI, currentJ];
                int newDist = dist[currentI, currentK] + dist[currentK, currentJ];

                if (newDist < oldDist &&
                    dist[currentI, currentK] < 99999 &&
                    dist[currentK, currentJ] < 99999)
                {
                    dist[currentI, currentJ] = newDist;
                    next[currentI, currentJ] = next[currentI, currentK];
                    state = AlgorithmState.Updating;
                }
                else
                {
                    MoveToNextCell();
                }
                isAnimating = true;
                break;

            case AlgorithmState.Updating:
                MoveToNextCell();
                state = AlgorithmState.ProcessingJ;
                isAnimating = true;
                break;
        }
    }

    private void MoveToNextCell()
    {
        currentJ++;
        if (currentJ >= nodeCount)
        {
            currentJ = 0;
            currentI++;
            if (currentI >= nodeCount)
            {
                currentI = 0;
                currentK++;
                if (currentK >= nodeCount)
                {
                    state = AlgorithmState.Completed;
                    isPaused = true;
                    autoStepping = false;
                }
                else
                {
                    state = AlgorithmState.ProcessingK;
                }
            }
            else
            {
                state = AlgorithmState.ProcessingI;
            }
        }
        else
        {
            state = AlgorithmState.ProcessingJ;
        }
    }

    // ==================== 绘制方法 ====================
    private void Draw()
    {
        Raylib.BeginDrawing();
        Raylib.ClearBackground(new Color(240, 240, 245, 255));

        DrawHeader();
        DrawGraph();
        DrawMatrix();
        DrawButtons();
        DrawLegend();
        DrawStatus();

        Raylib.EndDrawing();
    }

    private void DrawHeader()
    {
        Raylib.DrawText(TITLE, PADDING, TITLE_Y, TITLE_FONT_SIZE, Color.DarkBlue);
        Raylib.DrawText(INSTRUCTIONS, PADDING, INSTRUCTIONS_Y, TEXT_FONT_SIZE, Color.DarkGray);
    }

    private void DrawGraph()
    {
        Raylib.DrawRectangleRec(graphArea, Color.White);
        Raylib.DrawRectangleLinesEx(graphArea, 2, Color.Gray);
        Raylib.DrawText(GRAPH_TITLE, (int)graphArea.X + 10, (int)graphArea.Y - 30, SUBTITLE_FONT_SIZE, Color.Black);

        // 绘制所有边
        for (int i = 0; i < nodeCount; i++)
        {
            for (int j = 0; j < nodeCount; j++)
            {
                if (graph[i, j] < 99999 && i != j)
                {
                    DrawEdge(i, j, Color.Gray, graph[i, j].ToString(), false);
                }
            }
        }

        // 高亮当前处理的边
        if (state == AlgorithmState.ProcessingJ || state == AlgorithmState.Updating)
        {
            if (currentI != currentJ)
                DrawEdge(currentI, currentJ, Color.Red,
                        dist[currentI, currentJ] < 99999 ? dist[currentI, currentJ].ToString() : "∞", true);

            if (currentI != currentK && dist[currentI, currentK] < 99999)
                DrawEdge(currentI, currentK, Color.Blue, dist[currentI, currentK].ToString(), true);

            if (currentK != currentJ && dist[currentK, currentJ] < 99999)
                DrawEdge(currentK, currentJ, Color.Green, dist[currentK, currentJ].ToString(), true);
        }

        // 绘制节点
        for (int i = 0; i < nodeCount; i++)
        {
            DrawNode(i);
        }
    }

    private void DrawEdge(int from, int to, Color color, string weight, bool highlight)
    {
        Vector2 fromPos = nodePositions[from];
        Vector2 toPos = nodePositions[to];

        Vector2 direction = Vector2.Normalize(toPos - fromPos);
        float nodeRadius = 25;
        Vector2 start = fromPos + direction * nodeRadius;
        Vector2 end = toPos - direction * nodeRadius;

        Raylib.DrawLineEx(start, end, highlight ? 4 : 2, color);
        DrawArrow(start, end, color);

        Vector2 midPoint = (start + end) / 2;
        Vector2 textPos = midPoint + new Vector2(0, -15);
        Raylib.DrawText(weight, (int)textPos.X - 10, (int)textPos.Y - 10, SMALL_TEXT_FONT_SIZE, color);
    }

    private void DrawArrow(Vector2 start, Vector2 end, Color color)
    {
        Vector2 direction = Vector2.Normalize(end - start);
        Vector2 perpendicular = new Vector2(-direction.Y, direction.X);

        Vector2 arrowHead = end;
        Vector2 arrowLeft = end - direction * 10 + perpendicular * 5;
        Vector2 arrowRight = end - direction * 10 - perpendicular * 5;

        Raylib.DrawTriangle(arrowHead, arrowLeft, arrowRight, color);
    }

    private void DrawNode(int nodeIndex)
    {
        Vector2 position = nodePositions[nodeIndex];
        float radius = 25;

        Color nodeColor = nodeColors[nodeIndex % nodeColors.Length];

        // 高亮当前处理的节点
        if (nodeIndex == currentK && (state == AlgorithmState.ProcessingK || state == AlgorithmState.ProcessingI))
            Raylib.DrawCircle((int)position.X, (int)position.Y, radius + 3, Color.Yellow);
        else if (nodeIndex == currentI && state == AlgorithmState.ProcessingI)
            Raylib.DrawCircle((int)position.X, (int)position.Y, radius + 3, Color.Orange);
        else if (nodeIndex == currentJ && state == AlgorithmState.ProcessingJ)
            Raylib.DrawCircle((int)position.X, (int)position.Y, radius + 3, Color.Pink);

        Raylib.DrawCircle((int)position.X, (int)position.Y, radius, nodeColor);

        string nodeText = $"V{nodeIndex}";
        Vector2 textSize = Raylib.MeasureTextEx(Raylib.GetFontDefault(), nodeText, TEXT_FONT_SIZE, 1);
        Vector2 textPos = position - textSize / 2;
        Raylib.DrawText(nodeText, (int)textPos.X, (int)textPos.Y, TEXT_FONT_SIZE, Color.White);
    }

    private void DrawMatrix()
    {
        Raylib.DrawRectangleRec(matrixArea, Color.White);
        Raylib.DrawRectangleLinesEx(matrixArea, 2, Color.Gray);

        string title = showDistances ? MATRIX_TITLE_DIST : MATRIX_TITLE_PATH;
        Raylib.DrawText(title, (int)matrixArea.X + 10, (int)matrixArea.Y - 30, SUBTITLE_FONT_SIZE, Color.Black);

        int cellSize = 50;
        int startX = (int)matrixArea.X + 60;
        int startY = (int)matrixArea.Y + 60;

        // 绘制列标签
        for (int i = 0; i < nodeCount; i++)
        {
            Raylib.DrawText($"V{i}", startX + i * cellSize + cellSize / 2 - 10, startY - 30, TEXT_FONT_SIZE, Color.DarkBlue);
            Raylib.DrawText($"V{i}", startX - 40, startY + i * cellSize + cellSize / 2 - 10, TEXT_FONT_SIZE, Color.DarkBlue);
        }

        // 绘制矩阵单元格
        for (int i = 0; i < nodeCount; i++)
        {
            for (int j = 0; j < nodeCount; j++)
            {
                int cellX = startX + j * cellSize;
                int cellY = startY + i * cellSize;
                Rectangle cellRect = new Rectangle(cellX, cellY, cellSize, cellSize);

                Color cellColor = Color.White;
                if (i == currentK && j == currentK && state == AlgorithmState.ProcessingK)
                    cellColor = Color.Yellow;
                else if (i == currentI && state == AlgorithmState.ProcessingI)
                    cellColor = Color.Orange;
                else if (j == currentJ && state == AlgorithmState.ProcessingJ)
                    cellColor = Color.Pink;
                else if (i == currentI && j == currentJ &&
                         (state == AlgorithmState.ProcessingJ || state == AlgorithmState.Updating))
                    cellColor = Color.Red;

                Raylib.DrawRectangleRec(cellRect, cellColor);
                Raylib.DrawRectangleLinesEx(cellRect, 1, Color.Gray);

                string value;
                if (showDistances)
                {
                    value = dist[i, j] < 99999 ? dist[i, j].ToString() : "∞";
                }
                else
                {
                    value = next[i, j] >= 0 ? next[i, j].ToString() : "-";
                }

                Vector2 textSize = Raylib.MeasureTextEx(Raylib.GetFontDefault(), value, TEXT_FONT_SIZE, 1);
                Vector2 textPos = new Vector2(
                    cellX + cellSize / 2 - textSize.X / 2,
                    cellY + cellSize / 2 - textSize.Y / 2
                );

                Raylib.DrawText(value, (int)textPos.X, (int)textPos.Y, TEXT_FONT_SIZE, Color.Black);
            }
        }

        string operation = GetCurrentOperation();
        Raylib.DrawText(operation, (int)matrixArea.X + 10, (int)(matrixArea.Y + matrixArea.Height - 40),
                        TEXT_FONT_SIZE, Color.DarkBlue);
    }

    private string GetCurrentOperation()
    {
        switch (state)
        {
            case AlgorithmState.ProcessingK:
                return string.Format(STATUS_PROCESSING_K, currentK);
            case AlgorithmState.ProcessingI:
                return string.Format(STATUS_PROCESSING_I, currentI);
            case AlgorithmState.ProcessingJ:
                if (currentI == currentK || currentJ == currentK)
                    return string.Format(STATUS_PROCESSING_J_DIRECT, currentI, currentJ, dist[currentI, currentJ]);

                int sum = dist[currentI, currentK] + dist[currentK, currentJ];
                return string.Format(STATUS_PROCESSING_J_COMPARE,
                    currentI, currentJ, currentK,
                    dist[currentI, currentJ], dist[currentI, currentK], dist[currentK, currentJ], sum);
            case AlgorithmState.Updating:
                return string.Format(STATUS_UPDATING,
                    currentI, currentJ,
                    dist[currentI, currentK], dist[currentK, currentJ], dist[currentI, currentJ]);
            case AlgorithmState.Completed:
                return STATUS_COMPLETED;
            default:
                return STATUS_IDLE;
        }
    }

    private void DrawButtons()
    {
        foreach (var button in buttons)
        {
            button.Draw();
        }
    }

    private void DrawLegend()
    {
        Raylib.DrawText(LEGEND_TITLE, LEGEND_X, LEGEND_Y, SUBTITLE_FONT_SIZE, Color.Black);

        Raylib.DrawText(NODE_LABEL, LEGEND_X, LEGEND_Y + 35, TEXT_FONT_SIZE, Color.Black);
        for (int i = 0; i < Math.Min(5, nodeCount); i++)
        {
            Raylib.DrawCircle(LEGEND_X + 60 + i * 40, LEGEND_Y + 70, 12, nodeColors[i]);
            Raylib.DrawText($"V{i}", LEGEND_X + 50 + i * 40, LEGEND_Y + 65, SMALL_TEXT_FONT_SIZE, Color.Black);
        }

        Raylib.DrawText(PROCESSING_LABEL, LEGEND_X + 250, LEGEND_Y, TEXT_FONT_SIZE, Color.Black);
        Raylib.DrawText(LEGEND_K, LEGEND_X + 250, LEGEND_Y + 30, SMALL_TEXT_FONT_SIZE, Color.Yellow);
        Raylib.DrawText(LEGEND_I, LEGEND_X + 250, LEGEND_Y + 60, SMALL_TEXT_FONT_SIZE, Color.Orange);
        Raylib.DrawText(LEGEND_J, LEGEND_X + 250, LEGEND_Y + 90, SMALL_TEXT_FONT_SIZE, Color.Pink);
        Raylib.DrawText(LEGEND_CELL, LEGEND_X + 250, LEGEND_Y + 120, SMALL_TEXT_FONT_SIZE, Color.Red);
    }

    private void DrawStatus()
    {
        string statusText = $"Algorithm State: {state}";
        Raylib.DrawText(statusText, STATUS_X, STATUS_Y, SUBTITLE_FONT_SIZE, Color.DarkBlue);

        if (state != AlgorithmState.Idle && state != AlgorithmState.Completed)
        {
            Raylib.DrawText($"Current Indices: K={currentK}, I={currentI}, J={currentJ}",
                           STATUS_X, STATUS_Y + 30, TEXT_FONT_SIZE, Color.Black);
        }

        if (showPaths && state == AlgorithmState.Completed)
        {
            Raylib.DrawText(STATUS_SHORTEST_PATHS, STATUS_X, STATUS_Y + 60, TEXT_FONT_SIZE, Color.DarkGreen);

            int pathCount = 0;
            for (int i = 0; i < nodeCount && pathCount < 3; i++)
            {
                for (int j = 0; j < nodeCount && pathCount < 3; j++)
                {
                    if (i != j && dist[i, j] < 99999)
                    {
                        string path = GetPathString(i, j);
                        Raylib.DrawText(string.Format(STATUS_PATH_FORMAT, i, j, path, dist[i, j]),
                                       STATUS_X, STATUS_Y + 90 + pathCount * 25, SMALL_TEXT_FONT_SIZE, Color.DarkGreen);
                        pathCount++;
                    }
                }
            }
        }
    }

    private string GetPathString(int start, int end)
    {
        if (dist[start, end] == 99999) return STATUS_UNREACHABLE;

        string path = $"V{start}";
        int current = start;

        while (current != end)
        {
            current = next[current, end];
            path += $" -> V{current}";
        }

        return path;
    }

    // ==================== 按钮回调方法 ====================
    private void StartAlgorithm()
    {
        if (state == AlgorithmState.Completed)
        {
            ResetAlgorithm();
        }

        // 切换自动步进状态
        autoStepping = !autoStepping;

        if (autoStepping)
        {
            // 如果当前没有动画，立即开始执行下一步
            if (!isAnimating && state != AlgorithmState.Completed)
            {
                stepTimer = 0; // 重置自动步进计时器
            }

            buttons[0].Text = BTN_PAUSE;
            buttons[0].Color = Color.Red;
        }
        else
        {
            buttons[0].Text = BTN_START;
            buttons[0].Color = Color.Green;
        }
    }

    private void StepAlgorithm()
    {
        if (state == AlgorithmState.Completed) return;

        // 手动步进时，停止自动步进
        autoStepping = false;
        buttons[0].Text = BTN_START;
        buttons[0].Color = Color.Green;

        // 如果没有动画，立即执行下一步
        if (!isAnimating)
        {
            ExecuteNextStep();
        }
        // 如果正在动画中，等动画结束后不会自动执行下一步
    }

    private void ResetAlgorithm()
    {
        state = AlgorithmState.Idle;
        currentK = -1;
        currentI = -1;
        currentJ = -1;
        isPaused = true;
        isAnimating = false;
        animationTimer = 0;
        autoStepping = false;
        stepTimer = 0;

        // 重置按钮状态
        buttons[0].Text = BTN_START;
        buttons[0].Color = Color.Green;

        // 重新初始化矩阵
        InitializeMatrices();
    }

    private void ToggleMatrix()
    {
        showDistances = !showDistances;
        buttons[3].Text = showDistances ? BTN_SHOW_PATH : BTN_SHOW_DIST;
    }

    private void TogglePaths()
    {
        showPaths = !showPaths;
        buttons[4].Text = showPaths ? BTN_HIDE_PATH : BTN_TOGGLE_PATHS;
    }
}