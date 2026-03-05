using System;
using System.Collections.Generic;
using System.Numerics;
using Raylib_cs;

namespace HexagonalGridBFS
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
        public bool IsUpward { get; set; }
        public int HexagonId { get; set; } = -1; // 所属六边形ID
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

    public class HexagonNode
    {
        public int Id { get; set; }
        public Vector2 Center { get; set; }
        public List<int> TriangleIds { get; set; } // 组成六边形的三角形ID
        public NodeState State { get; set; }
        public List<int> Neighbors { get; set; }
        public int ParentId { get; set; } = -1;
        public int Distance { get; set; } = int.MaxValue;
        public (int q, int r) GridPos { get; set; } // 轴向坐标

        public HexagonNode()
        {
            TriangleIds = new List<int>();
            Neighbors = new List<int>();
            State = NodeState.Normal;
        }

        public bool ContainsPoint(Vector2 point, List<TriangleNode> triangles)
        {
            // 检查点是否在六边形的任何一个三角形中
            foreach (int triId in TriangleIds)
            {
                if (triId < triangles.Count && triangles[triId].ContainsPoint(point))
                    return true;
            }
            return false;
        }
    }

    public class HexagonalGridBFS
    {
        private const int ScreenWidth = 1200;
        private const int ScreenHeight = 800;
        private const float TriangleSide = 40.0f;
        private const float TriangleHeight = TriangleSide * 0.8660254f;

        // 六边形网格参数 - 使用更少的行列以清晰显示
        private const int HexGridRows = 8;
        private const int HexGridCols = 12;
        private const float StartX = 80;
        private const float StartY = 80;

        private List<TriangleNode> triangleNodes;
        private List<HexagonNode> hexagonNodes;
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
            Raylib.InitWindow(ScreenWidth, ScreenHeight, "BFS Shortest Path on Hexagonal Grid");
            Raylib.SetTargetFPS(60);

            GenerateHexagonalGrid();
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

        private void GenerateHexagonalGrid()
        {
            triangleNodes = new List<TriangleNode>();
            hexagonNodes = new List<HexagonNode>();
            bfsQueue = new Queue<int>();

            // 生成六边形网格的三角形
            GenerateHexagonalTriangles();

            // 建立六边形邻居关系
            BuildHexagonNeighbors();

            Console.WriteLine($"生成的三角形数量：{triangleNodes.Count}");
            Console.WriteLine($"生成的六边形数量：{hexagonNodes.Count}");
        }

        private void GenerateHexagonalTriangles()
        {
            triangleNodes.Clear();
            hexagonNodes.Clear();

            int hexagonId = 0;

            for (int r = 0; r < HexGridRows; r++)
            {
                for (int q = 0; q < HexGridCols; q++)
                {
                    // pointy-top, odd-col offset
                    float offset = (q % 2 == 1) ? TriangleHeight : 0f;
                    float centerX = StartX + q * TriangleSide * 1.5f;
                    float centerY = StartY + r * TriangleHeight * 2 + offset;

                    var hexNode = new HexagonNode
                    {
                        Id = hexagonId,
                        Center = new Vector2(centerX, centerY),
                        GridPos = (q, r)   // 注意：这里用 (q, r)，q=列, r=行
                    };

                    // 这里可以选择：要不要真的生成6个三角形
                    // 如果只做视觉效果，可以生成，但BFS不用它们
                    // 为简单起见，暂时保留你的6三角形生成，但注意它们不用于移动
                    for (int i = 0; i < 6; i++)
                    {
                        int triId = triangleNodes.Count;
                        var tri = new TriangleNode
                        {
                            Id = triId,
                            HexagonId = hexagonId
                        };

                        float a1 = MathF.PI / 3f * i;
                        float a2 = MathF.PI / 3f * (i + 1);

                        tri.Vertices[0] = hexNode.Center;

                        tri.Vertices[1] = new Vector2(
                            centerX + TriangleSide * MathF.Cos(a1),
                            centerY + TriangleSide * MathF.Sin(a1)
                        );

                        tri.Vertices[2] = new Vector2(
                            centerX + TriangleSide * MathF.Cos(a2),
                            centerY + TriangleSide * MathF.Sin(a2)
                        );

                        tri.Center = new Vector2(
                            (tri.Vertices[0].X + tri.Vertices[1].X + tri.Vertices[2].X) / 3f,
                            (tri.Vertices[0].Y + tri.Vertices[1].Y + tri.Vertices[2].Y) / 3f
                        );

                        // 判断 IsUpward（可选，如果你绘制需要区分方向）
                        float minY = MathF.Min(MathF.Min(tri.Vertices[0].Y, tri.Vertices[1].Y), tri.Vertices[2].Y);
                        float maxY = MathF.Max(MathF.Max(tri.Vertices[0].Y, tri.Vertices[1].Y), tri.Vertices[2].Y);
                        tri.IsUpward = tri.Center.Y < (minY + maxY) / 2f;

                        triangleNodes.Add(tri);
                        hexNode.TriangleIds.Add(triId);
                    }

                    hexagonNodes.Add(hexNode);
                    hexagonId++;
                }
            }

            BuildHexagonNeighbors();   // 下面会改这个
        }

        private void BuildTriangleNeighbors()
        {
            // 基于几何位置检测建立邻居关系
            for (int i = 0; i < triangleNodes.Count; i++)
            {
                triangleNodes[i].Neighbors.Clear();

                for (int j = 0; j < triangleNodes.Count; j++)
                {
                    if (i == j) continue;

                    // 检查两个三角形是否相邻（共享至少两个顶点）
                    int sharedVertices = 0;
                    for (int vi = 0; vi < 3; vi++)
                    {
                        for (int vj = 0; vj < 3; vj++)
                        {
                            if (Vector2.DistanceSquared(triangleNodes[i].Vertices[vi], triangleNodes[j].Vertices[vj]) < 1.0f)
                            {
                                sharedVertices++;
                            }
                        }
                    }

                    // 如果共享至少两个顶点，说明是邻居（共享一条边）
                    if (sharedVertices >= 2)
                    {
                        triangleNodes[i].Neighbors.Add(j);
                    }
                }
            }
        }

        private void BuildHexagonNeighbors()
        {
            // Pointy-top + odd-q layout (你的偏移：奇列向下)
            // 但为了匹配你的视觉“下= r+”，我们翻转 even/odd 表
            var directionsEvenQ = new (int dq, int dr)[]
            {
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1, -1),   // ← 关键改动：左上
    ( 0, +1)    // 正下
            };
            var directionsOddQ = new (int dq, int dr)[]
            {
    ( 1,  0),    // 东 → (6,3)
    ( 0, -1),    // 上 / 右上 → (5,2)
    (-1,  0),    // 西 → (4,3)
    (-1, +1),    // 左下 → (4,4)     ← 加这个补 (4,4)
    ( 0, +1),    // 下 → (5,4)
    ( 1, +1)     // 右下 → (6,4)
            };

            var posToId = hexagonNodes.ToDictionary(h => h.GridPos, h => h.Id);

            foreach (var hex in hexagonNodes)
            {
                hex.Neighbors.Clear();

                var dirs = (hex.GridPos.q % 2 == 0) ? directionsEvenQ : directionsOddQ;

                foreach (var (dq, dr) in dirs)
                {
                    int nq = hex.GridPos.q + dq;
                    int nr = hex.GridPos.r + dr;

                    if (posToId.TryGetValue((nq, nr), out int nid))
                    {
                        hex.Neighbors.Add(nid);
                    }
                }
            }

            // 打印验证（保留这个）
            var center = hexagonNodes.FirstOrDefault(h => h.GridPos.q == 6 && h.GridPos.r == 4);
            if (center != null)
            {
                Console.WriteLine($"中心 ({center.GridPos.q},{center.GridPos.r}) 邻居:");
                foreach (int nid in center.Neighbors)
                {
                    var n = hexagonNodes[nid];
                    Console.WriteLine($"  → ({n.GridPos.q},{n.GridPos.r})");
                }
            }
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

            if (Raylib.IsMouseButtonPressed(MouseButton.Left))
            {
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
                    HandleGridClick(mousePos, false);
                }
            }
            else if (Raylib.IsMouseButtonPressed(MouseButton.Right))
            {
                HandleGridClick(mousePos, true);
            }

            // 键盘控制
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
            // 找到被点击的三角形
            TriangleNode clickedTriangle = null;
            int clickedTriangleId = -1;

            for (int i = 0; i < triangleNodes.Count; i++)
            {
                if (triangleNodes[i].ContainsPoint(mousePos))
                {
                    clickedTriangle = triangleNodes[i];
                    clickedTriangleId = i;
                    break;
                }
            }

            if (clickedTriangle == null) return;

            // 找到对应的六边形
            int hexagonId = clickedTriangle.HexagonId;
            if (hexagonId == -1 || hexagonId >= hexagonNodes.Count) return;

            HexagonNode clickedHexagon = hexagonNodes[hexagonId];
            int clickedNodeId = hexagonId;

            if (isRightClick)
            {
                // 右键：重置节点状态
                if (clickedHexagon.State == NodeState.Start)
                {
                    startNodeId = -1;
                }
                else if (clickedHexagon.State == NodeState.End)
                {
                    endNodeId = -1;
                }

                clickedHexagon.State = NodeState.Normal;
                clickedHexagon.ParentId = -1;
                clickedHexagon.Distance = int.MaxValue;

                // 同时更新所有相关三角形的状态
                foreach (int triId in clickedHexagon.TriangleIds)
                {
                    if (triId < triangleNodes.Count)
                    {
                        triangleNodes[triId].State = NodeState.Normal;
                    }
                }

                statusMessage = "Node cleared.";
                return;
            }

            bool shiftPressed = Raylib.IsKeyDown(KeyboardKey.LeftShift) ||
                               Raylib.IsKeyDown(KeyboardKey.RightShift);

            if (shiftPressed)
            {
                // Shift+点击：设置/清除障碍物
                if (clickedHexagon.State == NodeState.Start || clickedHexagon.State == NodeState.End)
                {
                    statusMessage = "Cannot set Start or End as obstacle!";
                    return;
                }

                if (clickedHexagon.State == NodeState.Obstacle)
                {
                    clickedHexagon.State = NodeState.Normal;
                    statusMessage = "Obstacle cleared.";
                }
                else
                {
                    clickedHexagon.State = NodeState.Obstacle;
                    statusMessage = "Obstacle set. Use Shift+Click to clear.";
                }

                // 更新所有相关三角形的状态
                foreach (int triId in clickedHexagon.TriangleIds)
                {
                    if (triId < triangleNodes.Count)
                    {
                        triangleNodes[triId].State = clickedHexagon.State;
                    }
                }
                return;
            }

            // 普通左键点击：设置起点或终点
            if (clickedHexagon.State == NodeState.Start)
            {
                // 清除起点
                clickedHexagon.State = NodeState.Normal;
                startNodeId = -1;

                foreach (int triId in clickedHexagon.TriangleIds)
                {
                    if (triId < triangleNodes.Count)
                    {
                        triangleNodes[triId].State = NodeState.Normal;
                    }
                }

                statusMessage = "Start point cleared.";
            }
            else if (clickedHexagon.State == NodeState.End)
            {
                // 清除终点
                clickedHexagon.State = NodeState.Normal;
                endNodeId = -1;

                foreach (int triId in clickedHexagon.TriangleIds)
                {
                    if (triId < triangleNodes.Count)
                    {
                        triangleNodes[triId].State = NodeState.Normal;
                    }
                }

                statusMessage = "End point cleared.";
            }
            else if (clickedHexagon.State == NodeState.Obstacle)
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
                    if (startNodeId != -1 && startNodeId < hexagonNodes.Count)
                    {
                        hexagonNodes[startNodeId].State = NodeState.Normal;
                    }

                    startNodeId = clickedNodeId;
                    clickedHexagon.State = NodeState.Start;
                    clickedHexagon.Distance = 0;

                    foreach (int triId in clickedHexagon.TriangleIds)
                    {
                        if (triId < triangleNodes.Count)
                        {
                            triangleNodes[triId].State = NodeState.Start;
                        }
                    }

                    statusMessage = "Start point set (Green). Now click to set End point.";
                }
                else if (endNodeId == -1)
                {
                    // 设置终点
                    if (endNodeId != -1 && endNodeId < hexagonNodes.Count)
                    {
                        hexagonNodes[endNodeId].State = NodeState.Normal;
                    }

                    endNodeId = clickedNodeId;
                    clickedHexagon.State = NodeState.End;

                    foreach (int triId in clickedHexagon.TriangleIds)
                    {
                        if (triId < triangleNodes.Count)
                        {
                            triangleNodes[triId].State = NodeState.End;
                        }
                    }

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
            foreach (var hexNode in hexagonNodes)
            {
                if (hexNode.State != NodeState.Start && hexNode.State != NodeState.End && hexNode.State != NodeState.Obstacle)
                {
                    hexNode.State = NodeState.Normal;

                    // 更新对应的三角形状态
                    foreach (int triId in hexNode.TriangleIds)
                    {
                        if (triId < triangleNodes.Count)
                        {
                            triangleNodes[triId].State = NodeState.Normal;
                        }
                    }
                }
                hexNode.ParentId = -1;
                hexNode.Distance = int.MaxValue;
            }

            hexagonNodes[startNodeId].Distance = 0;
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
            HexagonNode currentNode = hexagonNodes[currentNodeId];

            if (currentNode.State != NodeState.Start)
            {
                currentNode.State = NodeState.Visited;

                // 更新对应的三角形状态
                foreach (int triId in currentNode.TriangleIds)
                {
                    if (triId < triangleNodes.Count && triangleNodes[triId].State != NodeState.Start && triangleNodes[triId].State != NodeState.End)
                    {
                        triangleNodes[triId].State = NodeState.Visited;
                    }
                }
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
                HexagonNode neighbor = hexagonNodes[neighborId];

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

                        // 更新对应的三角形状态
                        foreach (int triId in neighbor.TriangleIds)
                        {
                            if (triId < triangleNodes.Count && triangleNodes[triId].State != NodeState.End)
                            {
                                triangleNodes[triId].State = NodeState.Visiting;
                            }
                        }
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
                if (hexagonNodes[currentId].State != NodeState.End)
                {
                    hexagonNodes[currentId].State = NodeState.Path;

                    // 更新对应的三角形状态
                    foreach (int triId in hexagonNodes[currentId].TriangleIds)
                    {
                        if (triId < triangleNodes.Count && triangleNodes[triId].State != NodeState.End)
                        {
                            triangleNodes[triId].State = NodeState.Path;
                        }
                    }
                }
                currentId = hexagonNodes[currentId].ParentId;
            }
        }

        private void ResetGrid()
        {
            foreach (var hexNode in hexagonNodes)
            {
                hexNode.State = NodeState.Normal;
                hexNode.ParentId = -1;
                hexNode.Distance = int.MaxValue;

                // 更新对应的三角形状态
                foreach (int triId in hexNode.TriangleIds)
                {
                    if (triId < triangleNodes.Count)
                    {
                        triangleNodes[triId].State = NodeState.Normal;
                    }
                }
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
            foreach (var hexNode in hexagonNodes)
            {
                if (hexNode.State == NodeState.Obstacle)
                {
                    hexNode.State = NodeState.Normal;

                    // 更新对应的三角形状态
                    foreach (int triId in hexNode.TriangleIds)
                    {
                        if (triId < triangleNodes.Count)
                        {
                            triangleNodes[triId].State = NodeState.Normal;
                        }
                    }
                }
            }
            statusMessage = "All obstacles cleared.";
        }

        private void DrawGrid()
        {
            // 绘制所有三角形（作为六边形的组成部分）
            for (int i = 0; i < triangleNodes.Count; i++)
            {
                var node = triangleNodes[i];

                // 获取颜色（从六边形状态获取）
                Color fillColor = Color.LightGray; // 默认颜色

                // 如果有对应的六边形，使用六边形的状态
                if (node.HexagonId != -1 && node.HexagonId < hexagonNodes.Count)
                {
                    fillColor = GetNodeColor(hexagonNodes[node.HexagonId].State);
                }

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

                // 绘制节点信息（距离） - 显示六边形的距离
                if (node.HexagonId != -1 && node.HexagonId < hexagonNodes.Count)
                {
                    var hexNode = hexagonNodes[node.HexagonId];
                    if (hexNode.Distance < int.MaxValue && hexNode.State != NodeState.Start && hexNode.State != NodeState.End)
                    {
                        // 只在中心三角形上显示距离
                        bool isCenterTriangle = (i == hexNode.TriangleIds[0]); // 使用第一个三角形显示距离
                        if (isCenterTriangle)
                        {
                            string distanceText = hexNode.Distance.ToString();
                            Vector2 textPos = new Vector2(hexNode.Center.X - 5, hexNode.Center.Y - 5);
                            Raylib.DrawText(distanceText, (int)textPos.X, (int)textPos.Y, 12, Color.Black);
                        }
                    }
                    // 在绘制 hex 循环里加
                    Raylib.DrawText($"({hexNode.GridPos.q},{hexNode.GridPos.r})",(int)hexNode.Center.X - 20, (int)hexNode.Center.Y - 10, 10, Color.Black);
                }
            }

            // 绘制起点和终点的标记
            if (startNodeId != -1 && startNodeId < hexagonNodes.Count)
            {
                var startNode = hexagonNodes[startNodeId];
                Raylib.DrawText("S", (int)startNode.Center.X - 4, (int)startNode.Center.Y - 6, 14, Color.Black);
            }

            if (endNodeId != -1 && endNodeId < hexagonNodes.Count)
            {
                var endNode = hexagonNodes[endNodeId];
                Raylib.DrawText("E", (int)endNode.Center.X - 4, (int)endNode.Center.Y - 6, 14, Color.Black);
            }
        }

        private Color GetNodeColor(NodeState state)
        {
            // 使用非常鲜艳的颜色，确保可见
            switch (state)
            {
                case NodeState.Normal:
                    return new Color(240, 240, 240, 255); // 浅灰色
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
            DrawLegendItem("Normal", new Color(240, 240, 240, 255), 520);
            DrawLegendItem("Obstacle", new Color(105, 105, 105, 255), 540);
            DrawLegendItem("Visited", new Color(255, 255, 0, 255), 560);
            DrawLegendItem("Visiting", new Color(255, 165, 0, 255), 580);
            DrawLegendItem("Path", new Color(147, 112, 219, 255), 600);
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
            HexagonalGridBFS app = new HexagonalGridBFS();
            app.Run();
        }
    }
}