using System;
using System.Collections.Generic;
using System.Numerics;
using Raylib_cs;

namespace TriangularGridBFS
{
    public enum NodeState
    {
        Normal,      // 正常节点
        Start,       // 起点
        End,         // 终点
        Obstacle,    // 障碍物
        Visited,     // 已访问
        Visiting,    // 正在访问
        Path         // 最短路径
    }

    public class TriangleNode
    {
        public int Id { get; set; }
        public Vector2[] Vertices { get; set; }
        public Vector2 Center { get; set; }
        public bool IsUpward { get; set; } // 三角形方向：true=向上，false=向下
        public NodeState State { get; set; }
        public List<int> Neighbors { get; set; }
        public int ParentId { get; set; } = -1;
        public int Distance { get; set; } = int.MaxValue;

        public TriangleNode()
        {
            Vertices = new Vector2[3];
            Neighbors = new List<int>();
            State = NodeState.Normal;
        }

        public bool ContainsPoint(Vector2 point)
        {
            // 简化检测：先检查边界框
            float minX = Math.Min(Math.Min(Vertices[0].X, Vertices[1].X), Vertices[2].X);
            float maxX = Math.Max(Math.Max(Vertices[0].X, Vertices[1].X), Vertices[2].X);
            float minY = Math.Min(Math.Min(Vertices[0].Y, Vertices[1].Y), Vertices[2].Y);
            float maxY = Math.Max(Math.Max(Vertices[0].Y, Vertices[1].Y), Vertices[2].Y);

            if (point.X < minX || point.X > maxX || point.Y < minY || point.Y > maxY)
                return false;

            // 使用重心坐标法判断点是否在三角形内
            Vector2 v0 = Vertices[2] - Vertices[0];
            Vector2 v1 = Vertices[1] - Vertices[0];
            Vector2 v2 = point - Vertices[0];

            float dot00 = Vector2.Dot(v0, v0);
            float dot01 = Vector2.Dot(v0, v1);
            float dot02 = Vector2.Dot(v0, v2);
            float dot11 = Vector2.Dot(v1, v1);
            float dot12 = Vector2.Dot(v1, v2);

            float invDenom = 1.0f / (dot00 * dot11 - dot01 * dot01);
            float u = (dot11 * dot02 - dot01 * dot12) * invDenom;
            float v = (dot00 * dot12 - dot01 * dot02) * invDenom;

            return (u >= -0.01f) && (v >= -0.01f) && (u + v <= 1.01f);
        }
    }

    public class TriangularGridBFS
    {
        private const int ScreenWidth = 1200;
        private const int ScreenHeight = 800;
        private const float TriangleSide = 40.0f;
        private const float TriangleHeight = TriangleSide * 0.8660254f; // √3/2

        private const int GridRows = 15;  // 增加行数，确保最后一行也有三角形
        private const int GridCols = 20;  // 增加列数
        private const float StartX = 50;
        private const float StartY = 50;

        private List<TriangleNode> nodes;
        private Queue<int> bfsQueue;
        private bool isBFSRunning = false;
        private bool isBFSComplete = false;
        private bool isAutoStep = false;
        private float autoStepTimer = 0;
        private float autoStepInterval = 0.3f;

        private int startNodeId = -1;
        private int endNodeId = -1;

        // UI按钮
        private Rectangle startButton;
        private Rectangle stepButton;
        private Rectangle autoButton;
        private Rectangle resetButton;
        private Rectangle clearObstaclesButton;

        private string statusMessage = "Click to set START (Green), END (Red). Shift+Click for OBSTACLES.";

        public void Run()
        {
            Raylib.InitWindow(ScreenWidth, ScreenHeight, "BFS Shortest Path on Triangular Grid");
            Raylib.SetTargetFPS(60);

            InitializeTrueTriangularGrid();
            InitializeUI();

            while (!Raylib.WindowShouldClose())
            {
                ProcessInput();
                Update();

                Raylib.BeginDrawing();
                Raylib.ClearBackground(Color.RayWhite);

                DrawGrid();
                DrawUI();
                DrawStatus();

                Raylib.EndDrawing();
            }

            Raylib.CloseWindow();
        }

        private void InitializeTrueTriangularGrid()
        {
            nodes = new List<TriangleNode>();
            bfsQueue = new Queue<int>();

            // 关键改进：真正的交错三角形网格，每行错开半个边长
            int triangleId = 0;

            // 创建所有三角形，基于真正的交错排列
            for (int row = 0; row < GridRows; row++)
            {
                // 确定这一行的三角形朝向：奇数行以向下三角形开始，偶数行以向上三角形开始
                bool rowStartsWithUp = (row % 2 == 0);

                // 每行三角形数量：需要考虑交错排列
                int trianglesInRow = GridCols * 2; // 每行有2倍列数的三角形

                for (int col = 0; col < trianglesInRow; col++)
                {
                    // 根据列索引确定三角形朝向
                    bool isUpward = rowStartsWithUp ? (col % 2 == 0) : (col % 2 == 1);

                    TriangleNode node = new TriangleNode
                    {
                        Id = triangleId,
                        IsUpward = isUpward
                    };

                    // 计算三角形位置 - 关键改进：相邻行错开半个边长
                    // 基础水平位置
                    float xBase = StartX + col * TriangleSide / 2;

                    float rowOffset = 0;

                    // 最终x坐标
                    float x = xBase + rowOffset;

                    // y坐标：每行高度是三角形高度
                    float y = StartY + row * TriangleHeight;

                    // 根据朝向设置顶点
                    if (isUpward)
                    {
                        // 向上三角形
                        node.Vertices[0] = new Vector2(x, y + TriangleHeight);          // 左下
                        node.Vertices[1] = new Vector2(x + TriangleSide, y + TriangleHeight); // 右下
                        node.Vertices[2] = new Vector2(x + TriangleSide / 2, y);        // 上顶点

                        // 中心点
                        node.Center = new Vector2(
                            x + TriangleSide / 2,
                            y + TriangleHeight * 2 / 3
                        );
                    }
                    else
                    {
                        // 向下三角形
                        node.Vertices[0] = new Vector2(x, y);                            // 左上
                        node.Vertices[1] = new Vector2(x + TriangleSide, y);             // 右上
                        node.Vertices[2] = new Vector2(x + TriangleSide / 2, y + TriangleHeight); // 下顶点

                        // 中心点
                        node.Center = new Vector2(
                            x + TriangleSide / 2,
                            y + TriangleHeight / 3
                        );
                    }

                    node.State = NodeState.Normal;
                    nodes.Add(node);
                    triangleId++;
                }
            }

            // 建立邻居关系 - 基于几何位置检测
            BuildNeighborRelationshipsByGeometry();

            // 验证网格完整性
            ValidateGrid();
        }

        private void BuildNeighborRelationshipsByGeometry()
        {
            // 基于几何位置检测建立邻居关系
            for (int i = 0; i < nodes.Count; i++)
            {
                nodes[i].Neighbors.Clear();

                for (int j = 0; j < nodes.Count; j++)
                {
                    if (i == j) continue;

                    // 检查两个三角形是否相邻（共享至少两个顶点）
                    int sharedVertices = 0;
                    for (int vi = 0; vi < 3; vi++)
                    {
                        for (int vj = 0; vj < 3; vj++)
                        {
                            // 使用宽松的距离阈值，因为浮点数计算可能有误差
                            if (Vector2.DistanceSquared(nodes[i].Vertices[vi], nodes[j].Vertices[vj]) < 2.0f)
                            {
                                sharedVertices++;
                            }
                        }
                    }

                    // 如果共享至少两个顶点，说明是邻居（共享一条边）
                    if (sharedVertices >= 2)
                    {
                        nodes[i].Neighbors.Add(j);
                    }
                }
            }

            // 验证邻居关系
            int minNeighbors = int.MaxValue;
            int maxNeighbors = 0;
            int totalNeighbors = 0;

            for (int i = 0; i < nodes.Count; i++)
            {
                int neighborCount = nodes[i].Neighbors.Count;
                minNeighbors = Math.Min(minNeighbors, neighborCount);
                maxNeighbors = Math.Max(maxNeighbors, neighborCount);
                totalNeighbors += neighborCount;
            }

            Console.WriteLine($"邻居关系统计：最小邻居数={minNeighbors}, 最大邻居数={maxNeighbors}, 平均邻居数={(float)totalNeighbors / nodes.Count:F2}");
        }

        private void ValidateGrid()
        {
            Console.WriteLine($"总三角形数量：{nodes.Count}");

            // 检查网格覆盖范围
            float minX = float.MaxValue, maxX = float.MinValue;
            float minY = float.MaxValue, maxY = float.MinValue;

            foreach (var node in nodes)
            {
                foreach (var vertex in node.Vertices)
                {
                    if (vertex.X < minX) minX = vertex.X;
                    if (vertex.X > maxX) maxX = vertex.X;
                    if (vertex.Y < minY) minY = vertex.Y;
                    if (vertex.Y > maxY) maxY = vertex.Y;
                }
            }

            Console.WriteLine($"网格边界：X({minX:F1} ~ {maxX:F1}), Y({minY:F1} ~ {maxY:F1})");

            // 检查三角形密度
            int upwardCount = 0;
            int downwardCount = 0;

            foreach (var node in nodes)
            {
                if (node.IsUpward) upwardCount++;
                else downwardCount++;
            }

            Console.WriteLine($"三角形类型统计：向上={upwardCount}, 向下={downwardCount}");
        }

        private void InitializeUI()
        {
            int buttonWidth = 150;
            int buttonHeight = 40;
            int buttonSpacing = 10;
            int startX = ScreenWidth - buttonWidth - 20;
            int startY = 20;

            startButton = new Rectangle(startX, startY, buttonWidth, buttonHeight);
            stepButton = new Rectangle(startX, startY + buttonHeight + buttonSpacing, buttonWidth, buttonHeight);
            autoButton = new Rectangle(startX, startY + 2 * (buttonHeight + buttonSpacing), buttonWidth, buttonHeight);
            resetButton = new Rectangle(startX, startY + 3 * (buttonHeight + buttonSpacing), buttonWidth, buttonHeight);
            clearObstaclesButton = new Rectangle(startX, startY + 4 * (buttonHeight + buttonSpacing), buttonWidth, buttonHeight);
        }

        private void ProcessInput()
        {
            Vector2 mousePos = Raylib.GetMousePosition();

            // 处理网格点击
            if (Raylib.IsMouseButtonPressed(MouseButton.Left))
            {
                // 检查是否点击了按钮
                if (Raylib.CheckCollisionPointRec(mousePos, startButton))
                {
                    StartBFS();
                }
                else if (Raylib.CheckCollisionPointRec(mousePos, stepButton))
                {
                    StepBFS();
                }
                else if (Raylib.CheckCollisionPointRec(mousePos, autoButton))
                {
                    ToggleAutoStep();
                }
                else if (Raylib.CheckCollisionPointRec(mousePos, resetButton))
                {
                    ResetGrid();
                }
                else if (Raylib.CheckCollisionPointRec(mousePos, clearObstaclesButton))
                {
                    ClearObstacles();
                }
                else
                {
                    // 点击网格节点
                    HandleGridClick(mousePos, false);
                }
            }
            else if (Raylib.IsMouseButtonPressed(MouseButton.Right))
            {
                // 右键清除节点
                HandleGridClick(mousePos, true);
            }

            // 处理键盘输入
            if (Raylib.IsKeyPressed(KeyboardKey.Space))
            {
                if (isBFSRunning && !isAutoStep)
                {
                    StepBFS();
                }
                else
                {
                    StartBFS();
                }
            }
            else if (Raylib.IsKeyPressed(KeyboardKey.R))
            {
                ResetGrid();
            }
            else if (Raylib.IsKeyPressed(KeyboardKey.A))
            {
                ToggleAutoStep();
            }
        }

        private void HandleGridClick(Vector2 mousePos, bool isRightClick)
        {
            // 找到被点击的节点
            TriangleNode clickedNode = null;
            int clickedNodeId = -1;
            int nodesChecked = 0;

            for (int i = 0; i < nodes.Count; i++)
            {
                nodesChecked++;
                if (nodes[i].ContainsPoint(mousePos))
                {
                    clickedNode = nodes[i];
                    clickedNodeId = i;
                    break;
                }
            }

            // 调试信息
            if (clickedNode == null)
            {
                statusMessage = $"点击位置({mousePos.X:F0},{mousePos.Y:F0})无三角形。检查了{nodesChecked}个三角形。";
                Console.WriteLine($"点击检测：鼠标位置({mousePos.X:F1},{mousePos.Y:F1})，检查了{nodesChecked}个三角形");
                return;
            }

            Console.WriteLine($"点击到三角形{clickedNodeId}: 朝向={(clickedNode.IsUpward ? "上" : "下")}, 中心=({clickedNode.Center.X:F1},{clickedNode.Center.Y:F1})");

            if (isRightClick)
            {
                // 右键：重置节点状态
                if (clickedNode.State == NodeState.Start)
                {
                    startNodeId = -1;
                }
                else if (clickedNode.State == NodeState.End)
                {
                    endNodeId = -1;
                }

                clickedNode.State = NodeState.Normal;
                clickedNode.ParentId = -1;
                clickedNode.Distance = int.MaxValue;
                statusMessage = "Node cleared.";
                return;
            }

            // 检查是否按下了Shift键
            bool shiftPressed = Raylib.IsKeyDown(KeyboardKey.LeftShift) || Raylib.IsKeyDown(KeyboardKey.RightShift);

            if (shiftPressed)
            {
                // Shift+点击：设置/清除障碍物
                if (clickedNode.State == NodeState.Start || clickedNode.State == NodeState.End)
                {
                    statusMessage = "Cannot set Start or End as obstacle!";
                    return;
                }

                if (clickedNode.State == NodeState.Obstacle)
                {
                    clickedNode.State = NodeState.Normal;
                    statusMessage = "Obstacle cleared.";
                }
                else
                {
                    clickedNode.State = NodeState.Obstacle;
                    statusMessage = "Obstacle set. Use Shift+Click to clear.";
                }
                return;
            }

            // 普通左键点击：设置起点或终点
            if (clickedNode.State == NodeState.Start)
            {
                // 清除起点
                clickedNode.State = NodeState.Normal;
                startNodeId = -1;
                statusMessage = "Start point cleared.";
            }
            else if (clickedNode.State == NodeState.End)
            {
                // 清除终点
                clickedNode.State = NodeState.Normal;
                endNodeId = -1;
                statusMessage = "End point cleared.";
            }
            else if (clickedNode.State == NodeState.Obstacle)
            {
                // 不能将障碍物设为起点或终点
                statusMessage = "Cannot set obstacle as Start or End!";
            }
            else
            {
                // 设置新的起点或终点
                if (startNodeId == -1)
                {
                    // 设置起点
                    if (startNodeId != -1)
                    {
                        nodes[startNodeId].State = NodeState.Normal;
                    }

                    startNodeId = clickedNodeId;
                    clickedNode.State = NodeState.Start;
                    clickedNode.Distance = 0;
                    statusMessage = "Start point set (Green). Now click to set End point.";
                }
                else if (endNodeId == -1)
                {
                    // 设置终点
                    if (endNodeId != -1)
                    {
                        nodes[endNodeId].State = NodeState.Normal;
                    }

                    endNodeId = clickedNodeId;
                    clickedNode.State = NodeState.End;
                    statusMessage = "End point set (Red). Use Shift+Click to set obstacles.";
                }
                else
                {
                    // 已经有起点和终点，提示使用Shift设置障碍物
                    statusMessage = "Start and End already set. Use Shift+Click to set/clear obstacles.";
                }
            }
        }

        private void StartBFS()
        {
            if (startNodeId == -1 || endNodeId == -1)
            {
                statusMessage = "Please set both START and END nodes before running BFS.";
                return;
            }

            // 重置BFS状态
            foreach (var node in nodes)
            {
                if (node.State != NodeState.Start && node.State != NodeState.End && node.State != NodeState.Obstacle)
                {
                    node.State = NodeState.Normal;
                }
                node.ParentId = -1;
                node.Distance = int.MaxValue;
            }

            nodes[startNodeId].Distance = 0;
            bfsQueue.Clear();
            bfsQueue.Enqueue(startNodeId);
            isBFSRunning = true;
            isBFSComplete = false;
            statusMessage = "BFS started. Press SPACE to step through, or click Step/Auto.";
        }

        private void StepBFS()
        {
            if (!isBFSRunning || isBFSComplete || bfsQueue.Count == 0) return;

            // 处理当前节点
            int currentNodeId = bfsQueue.Dequeue();
            TriangleNode currentNode = nodes[currentNodeId];

            if (currentNode.State != NodeState.Start)
            {
                currentNode.State = NodeState.Visited;
            }

            // 检查是否到达终点
            if (currentNodeId == endNodeId)
            {
                isBFSComplete = true;
                TracePath();
                statusMessage = "BFS complete! Shortest path found (Purple).";
                return;
            }

            // 访问邻居
            foreach (int neighborId in currentNode.Neighbors)
            {
                TriangleNode neighbor = nodes[neighborId];

                // 跳过障碍物和已访问节点
                if (neighbor.State == NodeState.Obstacle || neighbor.State == NodeState.Visited ||
                    neighbor.State == NodeState.Start)
                    continue;

                if (neighbor.Distance > currentNode.Distance + 1)
                {
                    neighbor.Distance = currentNode.Distance + 1;
                    neighbor.ParentId = currentNodeId;
                    bfsQueue.Enqueue(neighborId);

                    if (neighbor.State != NodeState.End)
                    {
                        neighbor.State = NodeState.Visiting;
                    }
                }
            }

            statusMessage = $"BFS step: Distance={currentNode.Distance}, Queue={bfsQueue.Count}";
        }

        private void ToggleAutoStep()
        {
            isAutoStep = !isAutoStep;
            autoStepTimer = 0;
            statusMessage = isAutoStep ? "Auto-step enabled." : "Auto-step disabled.";
        }

        private void Update()
        {
            if (isAutoStep && isBFSRunning && !isBFSComplete)
            {
                autoStepTimer += Raylib.GetFrameTime();
                if (autoStepTimer >= autoStepInterval)
                {
                    autoStepTimer = 0;
                    StepBFS();
                }
            }
        }

        private void TracePath()
        {
            if (endNodeId == -1) return;

            int currentId = endNodeId;
            while (currentId != -1 && currentId != startNodeId)
            {
                if (nodes[currentId].State != NodeState.End)
                {
                    nodes[currentId].State = NodeState.Path;
                }
                currentId = nodes[currentId].ParentId;
            }
        }

        private void ResetGrid()
        {
            foreach (var node in nodes)
            {
                node.State = NodeState.Normal;
                node.ParentId = -1;
                node.Distance = int.MaxValue;
            }

            startNodeId = -1;
            endNodeId = -1;
            bfsQueue.Clear();
            isBFSRunning = false;
            isBFSComplete = false;
            isAutoStep = false;
            statusMessage = "Grid reset. Click to set START (Green), END (Red), or OBSTACLES.";
        }

        private void ClearObstacles()
        {
            foreach (var node in nodes)
            {
                if (node.State == NodeState.Obstacle)
                {
                    node.State = NodeState.Normal;
                }
            }
            statusMessage = "All obstacles cleared.";
        }

        private void DrawGrid()
        {
            // 调试：显示总节点数
            Raylib.DrawText($"Nodes: {nodes.Count}", ScreenWidth - 150, 10, 16, Color.DarkBlue);

            // 绘制所有三角形
            for (int i = 0; i < nodes.Count; i++)
            {
                var node = nodes[i];

                // 获取颜色
                Color fillColor = GetNodeColor(node.State, node.IsUpward);
                Color borderColor = Color.DarkGray;

                // 关键修复：针对向上和向下三角形使用不同的顶点顺序
                if (node.IsUpward)
                {
                    // 向上三角形：使用当前顶点顺序
                    Raylib.DrawTriangle(node.Vertices[0], node.Vertices[1], node.Vertices[2], fillColor);
                    Raylib.DrawTriangleLines(node.Vertices[0], node.Vertices[1], node.Vertices[2], borderColor);
                }
                else
                {
                    // 向下三角形：调整顶点顺序确保正确填充
                    // 尝试不同的顺序组合
                    Raylib.DrawTriangle(node.Vertices[0], node.Vertices[2], node.Vertices[1], fillColor);
                    Raylib.DrawTriangleLines(node.Vertices[0], node.Vertices[2], node.Vertices[1], borderColor);
                }

                // 绘制节点信息（距离）
                if (node.Distance < int.MaxValue && node.State != NodeState.Start && node.State != NodeState.End)
                {
                    string distanceText = node.Distance.ToString();
                    Vector2 textPos = new Vector2(node.Center.X - 5, node.Center.Y - 5);
                    Raylib.DrawText(distanceText, (int)textPos.X, (int)textPos.Y, 12, Color.Black);
                }

                // 调试：显示节点ID和状态
                if (node.State != NodeState.Normal)
                {
                    string stateText = node.State.ToString().Substring(0, 1);
                    Raylib.DrawText(stateText, (int)node.Center.X - 3, (int)node.Center.Y - 15, 10, Color.Black);
                }
            }

            // 绘制起点和终点的标记
            if (startNodeId != -1 && startNodeId < nodes.Count)
            {
                var startNode = nodes[startNodeId];
                Raylib.DrawText("S", (int)startNode.Center.X - 4, (int)startNode.Center.Y - 6, 14, Color.Black);
            }

            if (endNodeId != -1 && endNodeId < nodes.Count)
            {
                var endNode = nodes[endNodeId];
                Raylib.DrawText("E", (int)endNode.Center.X - 4, (int)endNode.Center.Y - 6, 14, Color.Black);
            }
        }

        private Color GetNodeColor(NodeState state, bool isUpward)
        {
            // 使用非常鲜艳的颜色，确保可见
            switch (state)
            {
                case NodeState.Normal:
                    // 向上和向下三角形使用不同的基础颜色
                    if (isUpward)
                        return new Color(173, 216, 230, 255); // 浅蓝色（向上）
                    else
                        return new Color(144, 238, 144, 255); // 浅绿色（向下）

                case NodeState.Start:
                    return new Color(0, 255, 0, 255); // 亮绿色

                case NodeState.End:
                    return new Color(255, 0, 0, 255); // 亮红色

                case NodeState.Obstacle:
                    return new Color(105, 105, 105, 255); // 深灰色

                case NodeState.Visited:
                    return new Color(255, 255, 0, 255); // 黄色

                case NodeState.Visiting:
                    return new Color(255, 165, 0, 255); // 橙色

                case NodeState.Path:
                    return new Color(147, 112, 219, 255); // 紫色

                default:
                    return Color.White;
            }
        }

        private void DrawUI()
        {
            // 绘制控制面板背景
            Raylib.DrawRectangle(ScreenWidth - 200, 0, 200, ScreenHeight, new Color(240, 240, 240, 230));

            // 绘制按钮
            DrawButton(startButton, "Start BFS", isBFSRunning ? Color.Gray : Color.DarkGreen);
            DrawButton(stepButton, "Step BFS", (!isBFSRunning || isBFSComplete) ? Color.Gray : Color.DarkBlue);
            DrawButton(autoButton, isAutoStep ? "Auto: ON" : "Auto: OFF", isAutoStep ? Color.Orange : Color.DarkBlue);
            DrawButton(resetButton, "Reset Grid", Color.Red);
            DrawButton(clearObstaclesButton, "Clear Obstacles", Color.DarkGray);

            // 绘制说明
            Raylib.DrawText("CONTROLS", ScreenWidth - 190, 280, 20, Color.DarkBlue);
            Raylib.DrawText("Left-click: Set Start/End", ScreenWidth - 190, 310, 16, Color.Black);
            Raylib.DrawText("Shift+click: Set Obstacle", ScreenWidth - 190, 330, 16, Color.Black);
            Raylib.DrawText("Right-click: Clear node", ScreenWidth - 190, 350, 16, Color.Black);
            Raylib.DrawText("SPACE: Start/Step BFS", ScreenWidth - 190, 370, 16, Color.Black);
            Raylib.DrawText("A: Toggle auto-step", ScreenWidth - 190, 390, 16, Color.Black);
            Raylib.DrawText("R: Reset grid", ScreenWidth - 190, 410, 16, Color.Black);

            // 绘制图例
            Raylib.DrawText("LEGEND", ScreenWidth - 190, 450, 20, Color.DarkBlue);
            DrawLegendItem("Start", new Color(0, 255, 0, 255), 480);
            DrawLegendItem("End", new Color(255, 0, 0, 255), 500);
            DrawLegendItem("Normal Up", new Color(173, 216, 230, 255), 520);
            DrawLegendItem("Normal Down", new Color(144, 238, 144, 255), 540);
            DrawLegendItem("Obstacle", new Color(105, 105, 105, 255), 560);
            DrawLegendItem("Visited", new Color(255, 255, 0, 255), 580);
            DrawLegendItem("Visiting", new Color(255, 165, 0, 255), 600);
            DrawLegendItem("Path", new Color(147, 112, 219, 255), 620);
        }

        private void DrawButton(Rectangle rect, string text, Color color)
        {
            Raylib.DrawRectangleRec(rect, color);
            Raylib.DrawRectangleLines((int)rect.X, (int)rect.Y, (int)rect.Width, (int)rect.Height, Color.Black);

            int textWidth = Raylib.MeasureText(text, 18);
            Raylib.DrawText(text, (int)(rect.X + rect.Width / 2 - textWidth / 2), (int)(rect.Y + 10), 18, Color.White);
        }

        private void DrawLegendItem(string text, Color color, int y)
        {
            Raylib.DrawRectangle(ScreenWidth - 185, y, 15, 15, color);
            Raylib.DrawRectangleLines(ScreenWidth - 185, y, 15, 15, Color.Black);
            Raylib.DrawText(text, ScreenWidth - 165, y - 2, 14, Color.Black);
        }

        private void DrawStatus()
        {
            Raylib.DrawRectangle(0, ScreenHeight - 40, ScreenWidth, 40, new Color(50, 50, 50, 220));
            Raylib.DrawText(statusMessage, 20, ScreenHeight - 30, 20, Color.White);

            // 显示算法状态
            string algoStatus = isBFSComplete ? "COMPLETE" : (isBFSRunning ? "RUNNING" : "READY");
            Color statusColor = isBFSComplete ? Color.Green : (isBFSRunning ? Color.Yellow : Color.White);
            Raylib.DrawText($"Status: {algoStatus}", ScreenWidth - 250, ScreenHeight - 30, 20, statusColor);
        }
    }

    class Program
    {
        static void Main()
        {
            TriangularGridBFS app = new TriangularGridBFS();
            app.Run();
        }
    }
}