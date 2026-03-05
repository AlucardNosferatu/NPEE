using System;
using System.Collections.Generic;
using System.Linq;
using Raylib_cs;

namespace IslandSweepVisualization
{
    public class Sweep
    {
        // 网格和算法状态
        private int[,] grid;
        private int rows, cols;

        // 算法执行状态
        private enum AlgorithmState
        {
            Ready,        // 准备开始
            Sweeping,     // 扫描中 - 处理当前行的连续1段
            Completed     // 完成
        }

        private AlgorithmState state = AlgorithmState.Ready;
        private int currentRow = 0;
        private int maxIslandArea = 0;

        // 岛屿数据结构
        private class Island
        {
            public int Id { get; }
            public int Area { get; set; }
            public List<(int start, int end)> LastRowSegments { get; set; } // 上一行的连续段
            public List<(int row, int start, int end)> AllSegments { get; set; } // 所有段的完整记录

            public Island(int id)
            {
                Id = id;
                Area = 0;
                LastRowSegments = new List<(int, int)>();
                AllSegments = new List<(int row, int start, int end)>();
            }

            // 检查是否与给定区间重叠
            public bool Overlaps(int start, int end)
            {
                foreach (var segment in LastRowSegments)
                {
                    if (end >= segment.start && start <= segment.end)
                        return true;
                }
                return false;
            }
        }

        private List<Island> islands = new List<Island>();
        private int nextIslandId = 1;
        private Dictionary<int, Color> islandColors = new Dictionary<int, Color>();

        // 当前行处理状态
        private List<(int start, int end)> currentRowSegments = new List<(int, int)>();
        private Dictionary<(int start, int end), List<Island>> segmentToIslands = new Dictionary<(int, int), List<Island>>();

        // 记录每个单元格所属的岛屿ID
        private int[,] cellIslandIds;

        // 网格显示参数
        private const int CellSize = 35;
        private const int GridMargin = 50;
        private const int ButtonWidth = 200;
        private const int ButtonHeight = 40;
        private const int ButtonMargin = 20;

        // 随机生成网格
        private void GenerateGrid()
        {
            Random rand = new Random();
            grid = new int[rows, cols];
            cellIslandIds = new int[rows, cols];

            // 随机生成0或1，1的概率约为40%
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    grid[i, j] = rand.Next(0, 100) < 40 ? 1 : 0;
                    cellIslandIds[i, j] = -1; // 初始化为-1，表示未分配岛屿
                }
            }

            ResetAlgorithm();
        }

        // 重置算法状态
        private void ResetAlgorithm()
        {
            state = AlgorithmState.Ready;
            currentRow = 0;
            maxIslandArea = 0;

            islands.Clear();
            nextIslandId = 1;
            islandColors.Clear();

            currentRowSegments.Clear();
            segmentToIslands.Clear();

            // 重置单元格岛屿ID
            if (cellIslandIds != null)
            {
                for (int i = 0; i < rows; i++)
                    for (int j = 0; j < cols; j++)
                        cellIslandIds[i, j] = -1;
            }
        }

        // 执行算法的一步
        private void StepAlgorithm()
        {
            switch (state)
            {
                case AlgorithmState.Ready:
                    state = AlgorithmState.Sweeping;
                    currentRow = 0;
                    PrepareCurrentRow();
                    break;

                case AlgorithmState.Sweeping:
                    if (currentRow >= rows)
                    {
                        state = AlgorithmState.Completed;
                        return;
                    }

                    // 处理当前行
                    ProcessCurrentRow();

                    // 移动到下一行
                    currentRow++;
                    if (currentRow < rows)
                    {
                        PrepareCurrentRow();
                    }
                    else
                    {
                        state = AlgorithmState.Completed;
                    }
                    break;

                case AlgorithmState.Completed:
                    // 算法已完成
                    break;
            }
        }

        // 准备当前行的扫描
        private void PrepareCurrentRow()
        {
            currentRowSegments.Clear();
            segmentToIslands.Clear();

            // 找出当前行的所有连续1段
            int col = 0;
            while (col < cols)
            {
                if (grid[currentRow, col] == 1)
                {
                    int start = col;
                    while (col < cols && grid[currentRow, col] == 1)
                    {
                        col++;
                    }
                    int end = col - 1;
                    currentRowSegments.Add((start, end));

                    // 找出与这个段重叠的岛屿
                    List<Island> overlapping = new List<Island>();
                    foreach (var island in islands)
                    {
                        if (island.Overlaps(start, end))
                        {
                            overlapping.Add(island);
                        }
                    }
                    segmentToIslands[(start, end)] = overlapping;
                }
                else
                {
                    col++;
                }
            }

            // 为没有重叠岛屿的段创建新岛屿
            foreach (var segment in currentRowSegments)
            {
                if (segmentToIslands[segment].Count == 0)
                {
                    Island newIsland = new Island(nextIslandId++);
                    islands.Add(newIsland);

                    // 分配颜色
                    if (!islandColors.ContainsKey(newIsland.Id))
                    {
                        islandColors[newIsland.Id] = GetColorForIsland(newIsland.Id);
                    }

                    segmentToIslands[segment] = new List<Island> { newIsland };
                }
            }
        }

        // 处理当前行
        private void ProcessCurrentRow()
        {
            // 第一步：处理需要合并的岛屿
            List<HashSet<Island>> mergeGroups = new List<HashSet<Island>>();

            // 找出通过当前行段连接的所有岛屿组
            foreach (var segment in currentRowSegments)
            {
                var segmentIslands = segmentToIslands[segment];
                if (segmentIslands.Count > 1)
                {
                    // 这个段连接了多个岛屿，需要检查是否已经在一个组中
                    bool foundGroup = false;
                    HashSet<Island> targetGroup = null;

                    foreach (var group in mergeGroups)
                    {
                        foreach (var island in segmentIslands)
                        {
                            if (group.Contains(island))
                            {
                                if (!foundGroup)
                                {
                                    targetGroup = group;
                                    foundGroup = true;
                                }
                                else if (targetGroup != group)
                                {
                                    // 合并两个组
                                    targetGroup.UnionWith(group);
                                    mergeGroups.Remove(group);
                                }
                                break;
                            }
                        }
                        if (foundGroup) break;
                    }

                    if (foundGroup)
                    {
                        // 将当前段的所有岛屿加入目标组
                        foreach (var island in segmentIslands)
                        {
                            targetGroup.Add(island);
                        }
                    }
                    else
                    {
                        // 创建新组
                        HashSet<Island> newGroup = new HashSet<Island>();
                        foreach (var island in segmentIslands)
                        {
                            newGroup.Add(island);
                        }
                        mergeGroups.Add(newGroup);
                    }
                }
            }

            // 第二步：合并岛屿
            foreach (var group in mergeGroups)
            {
                if (group.Count > 1)
                {
                    // 选择第一个岛屿作为合并目标
                    var targetIsland = group.First();
                    var islandsToMerge = group.Where(island => island != targetIsland).ToList();

                    foreach (var island in islandsToMerge)
                    {
                        // 合并面积
                        targetIsland.Area += island.Area;

                        // 合并段记录
                        targetIsland.AllSegments.AddRange(island.AllSegments);
                        targetIsland.LastRowSegments.AddRange(island.LastRowSegments);

                        // 更新所有被合并岛屿的单元格ID
                        foreach (var segment in island.AllSegments)
                        {
                            for (int col = segment.start; col <= segment.end; col++)
                            {
                                cellIslandIds[segment.row, col] = targetIsland.Id;
                            }
                        }

                        // 从列表中移除
                        islands.Remove(island);

                        // 更新segmentToIslands映射，将被合并的岛屿替换为目标岛屿
                        foreach (var segment in currentRowSegments)
                        {
                            var islandList = segmentToIslands[segment];
                            if (islandList.Contains(island))
                            {
                                islandList.Remove(island);
                                if (!islandList.Contains(targetIsland))
                                {
                                    islandList.Add(targetIsland);
                                }
                            }
                        }
                    }
                }
            }

            // 第三步：清空所有岛屿的上一行段信息，准备更新
            foreach (var island in islands)
            {
                island.LastRowSegments.Clear();
            }

            // 第四步：为每个段分配岛屿并更新信息
            foreach (var segment in currentRowSegments)
            {
                var segmentIslands = segmentToIslands[segment];

                // 处理合并后可能的重复
                var uniqueIslands = new HashSet<Island>(segmentIslands);
                Island targetIsland = uniqueIslands.First();

                // 计算当前段的长度
                int segmentLength = segment.end - segment.start + 1;

                // 检查这个段是否已经被计入面积（对于新岛屿，还没有被计入）
                // 我们只在岛屿还没有这个段的记录时才增加面积
                bool segmentAlreadyCounted = false;

                // 检查目标岛屿是否已经包含了当前行的这个段
                foreach (var existingSegment in targetIsland.AllSegments)
                {
                    if (existingSegment.row == currentRow &&
                        existingSegment.start == segment.start &&
                        existingSegment.end == segment.end)
                    {
                        segmentAlreadyCounted = true;
                        break;
                    }
                }

                // 如果没有被计入，则增加面积
                if (!segmentAlreadyCounted)
                {
                    targetIsland.Area += segmentLength;

                    // 记录这个段
                    targetIsland.AllSegments.Add((currentRow, segment.start, segment.end));
                }

                // 记录单元格所属的岛屿
                for (int col = segment.start; col <= segment.end; col++)
                {
                    cellIslandIds[currentRow, col] = targetIsland.Id;
                }

                // 更新岛屿的上一行段信息
                targetIsland.LastRowSegments.Add(segment);

                // 更新最大面积
                if (targetIsland.Area > maxIslandArea)
                {
                    maxIslandArea = targetIsland.Area;
                }
            }
        }

        // 运行完整的算法
        private void RunFullAlgorithm()
        {
            ResetAlgorithm();
            state = AlgorithmState.Sweeping;

            while (state != AlgorithmState.Completed)
            {
                StepAlgorithm();
            }
        }

        // 为岛屿分配颜色
        private Color GetColorForIsland(int islandId)
        {
            Color[] colors = new Color[]
            {
                Color.Red, Color.Green, Color.Blue, Color.Yellow,
                Color.Orange, Color.Purple, Color.Pink, Color.Lime,
                Color.SkyBlue, Color.Violet, Color.Gold, Color.Brown
            };

            return colors[(islandId - 1) % colors.Length];
        }

        // 获取单元格所属的岛屿ID
        private int GetCellIslandId(int row, int col)
        {
            if (grid[row, col] == 0) return -1;

            // 如果已经分配了岛屿ID，直接返回
            if (cellIslandIds[row, col] != -1)
            {
                return cellIslandIds[row, col];
            }

            // 对于已扫描的行，检查是否属于任何岛屿
            if (row <= currentRow)
            {
                foreach (var island in islands)
                {
                    foreach (var segment in island.AllSegments)
                    {
                        if (segment.row == row && col >= segment.start && col <= segment.end)
                            return island.Id;
                    }
                }
            }

            return -1;
        }

        // 绘制网格
        private void DrawGrid()
        {
            int startX = GridMargin;
            int startY = GridMargin;

            // 绘制网格背景和单元格
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    int x = startX + j * CellSize;
                    int y = startY + i * CellSize;

                    // 确定单元格颜色
                    Color cellColor;
                    int cellIslandId = GetCellIslandId(i, j);

                    if (grid[i, j] == 0)
                    {
                        // 海洋
                        cellColor = Color.Blue;
                    }
                    else if (cellIslandId != -1 && islandColors.ContainsKey(cellIslandId))
                    {
                        // 已分配岛屿的陆地
                        cellColor = islandColors[cellIslandId];
                    }
                    else if (i < currentRow || (i == currentRow && state == AlgorithmState.Completed))
                    {
                        // 已扫描但未分配岛屿的陆地（不应该发生）
                        cellColor = Color.DarkGray;
                    }
                    else
                    {
                        // 未扫描的陆地
                        cellColor = Color.DarkGreen;
                    }

                    // 绘制单元格
                    Raylib.DrawRectangle(x, y, CellSize, CellSize, cellColor);

                    // 高亮当前行
                    if (i == currentRow && state == AlgorithmState.Sweeping)
                    {
                        Raylib.DrawRectangleLines(x + 1, y + 1, CellSize - 2, CellSize - 2, Color.Yellow);
                    }

                    // 绘制网格线
                    Raylib.DrawRectangleLines(x, y, CellSize, CellSize, Color.Black);

                    // 显示单元格值
                    string cellText = grid[i, j].ToString();
                    int textWidth = Raylib.MeasureText(cellText, 16);
                    Raylib.DrawText(cellText,
                        x + CellSize / 2 - textWidth / 2,
                        y + CellSize / 2 - 8,
                        16, Color.White);
                }
            }

            // 绘制网格坐标标签
            for (int i = 0; i < rows; i++)
            {
                Raylib.DrawText($"R{i}",
                    GridMargin - 30,
                    GridMargin + i * CellSize + CellSize / 2 - 8,
                    14, Color.Black);
            }

            for (int j = 0; j < cols; j++)
            {
                Raylib.DrawText($"C{j}",
                    GridMargin + j * CellSize + CellSize / 2 - 8,
                    GridMargin - 30,
                    14, Color.Black);
            }

            // 绘制当前行的段信息
            if (state == AlgorithmState.Sweeping && currentRow < rows)
            {
                foreach (var segment in currentRowSegments)
                {
                    int x1 = startX + segment.start * CellSize;
                    int x2 = startX + (segment.end + 1) * CellSize;
                    int yPos = startY + currentRow * CellSize;

                    Raylib.DrawRectangleLines(x1, yPos, x2 - x1, CellSize, Color.Red);

                    // 显示段信息
                    string segmentText = $"{segment.start}-{segment.end}";
                    int textWidth = Raylib.MeasureText(segmentText, 14);
                    Raylib.DrawText(segmentText,
                        x1 + (x2 - x1) / 2 - textWidth / 2,
                        yPos - 20,
                        14, Color.Red);
                }
            }
        }

        // 绘制信息面板
        private void DrawInfoPanel()
        {
            int panelX = GridMargin + cols * CellSize + 50;
            int panelY = GridMargin;

            // 绘制面板背景
            Raylib.DrawRectangle(panelX, panelY, 350, 500, new Color(240, 240, 240, 255));
            Raylib.DrawRectangleLines(panelX, panelY, 350, 500, Color.DarkGray);

            // 标题
            Raylib.DrawText("Sweep Line Algorithm", panelX + 20, panelY + 20, 24, Color.DarkBlue);

            // 状态信息
            string stateText = $"State: {state}";
            Raylib.DrawText(stateText, panelX + 20, panelY + 60, 20, Color.Black);

            string currentRowText = $"Current Row: {currentRow}";
            Raylib.DrawText(currentRowText, panelX + 20, panelY + 90, 18, Color.Black);

            string islandsCountText = $"Islands Found: {islands.Count}";
            Raylib.DrawText(islandsCountText, panelX + 20, panelY + 120, 18, Color.Black);

            string maxAreaText = $"Max Island Area: {maxIslandArea}";
            Raylib.DrawText(maxAreaText, panelX + 20, panelY + 150, 18, Color.Black);

            // 当前行段信息
            Raylib.DrawText("Current Row Segments:", panelX + 20, panelY + 190, 18, Color.DarkBlue);

            int segmentY = 220;
            if (state == AlgorithmState.Sweeping && currentRow < rows)
            {
                foreach (var segment in currentRowSegments)
                {
                    string segmentInfo = $"[{segment.start}-{segment.end}]";
                    var overlappingIslands = segmentToIslands.ContainsKey(segment) ?
                        segmentToIslands[segment] : new List<Island>();

                    // 去重处理
                    var uniqueIslands = new HashSet<Island>(overlappingIslands);

                    if (uniqueIslands.Count == 0)
                    {
                        segmentInfo += " -> New Island";
                    }
                    else if (uniqueIslands.Count == 1)
                    {
                        segmentInfo += $" -> Island {uniqueIslands.First().Id}";
                    }
                    else
                    {
                        segmentInfo += $" -> Merge Islands: ";
                        foreach (var island in uniqueIslands)
                        {
                            segmentInfo += $"{island.Id} ";
                        }
                    }

                    Raylib.DrawText(segmentInfo, panelX + 30, panelY + segmentY, 16, Color.DarkGray);
                    segmentY += 25;
                }
            }
            else
            {
                Raylib.DrawText("No segments to process", panelX + 30, panelY + segmentY, 16, Color.DarkGray);
            }

            // 算法说明
            Raylib.DrawText("Algorithm Steps:", panelX + 20, panelY + 320, 18, Color.DarkBlue);

            string step1 = "1. Sweep through rows from top to bottom";
            string step2 = "2. Find contiguous segments of 1s in each row";
            string step3 = "3. Check overlap with previous row's island segments";
            string step4 = "4. Create new island if no overlap";
            string step5 = "5. Merge islands if segment connects multiple";
            string step6 = "6. Update island area and row segments";

            Raylib.DrawText(step1, panelX + 30, panelY + 350, 14, Color.DarkGray);
            Raylib.DrawText(step2, panelX + 30, panelY + 370, 14, Color.DarkGray);
            Raylib.DrawText(step3, panelX + 30, panelY + 390, 14, Color.DarkGray);
            Raylib.DrawText(step4, panelX + 30, panelY + 410, 14, Color.DarkGray);
            Raylib.DrawText(step5, panelX + 30, panelY + 430, 14, Color.DarkGray);
            Raylib.DrawText(step6, panelX + 30, panelY + 450, 14, Color.DarkGray);

            // 岛屿列表
            Raylib.DrawText("Islands:", panelX + 20, panelY + 480, 18, Color.DarkBlue);

            int islandY = 510;
            int displayCount = Math.Min(5, islands.Count);
            for (int i = 0; i < displayCount; i++)
            {
                var island = islands[i];
                string islandInfo = $"Island {island.Id}: Area = {island.Area}";
                Raylib.DrawText(islandInfo, panelX + 30, panelY + islandY, 14, Color.DarkGray);
                islandY += 20;
            }

            if (islands.Count > 5)
            {
                Raylib.DrawText($"... and {islands.Count - 5} more", panelX + 30, panelY + islandY, 14, Color.DarkGray);
            }
        }

        // 绘制控制按钮
        private void DrawControlButtons()
        {
            int buttonY = GridMargin + rows * CellSize + 30;

            // 单步执行按钮
            Rectangle stepButton = new Rectangle(GridMargin, buttonY, ButtonWidth, ButtonHeight);
            bool stepHover = Raylib.CheckCollisionPointRec(Raylib.GetMousePosition(), stepButton);
            Color stepColor = stepHover ? Color.LightGray : Color.Gray;

            Raylib.DrawRectangleRec(stepButton, stepColor);
            Raylib.DrawRectangleLines((int)stepButton.X, (int)stepButton.Y,
                (int)stepButton.Width, (int)stepButton.Height, Color.Black);

            string stepText = state == AlgorithmState.Completed ? "Algorithm Completed" : "Step (Next Row)";
            int stepTextWidth = Raylib.MeasureText(stepText, 20);
            Raylib.DrawText(stepText,
                (int)(stepButton.X + stepButton.Width / 2 - stepTextWidth / 2),
                (int)(stepButton.Y + 10),
                20, Color.Black);

            // 运行完整算法按钮
            Rectangle runButton = new Rectangle(
                GridMargin + ButtonWidth + ButtonMargin,
                buttonY, ButtonWidth, ButtonHeight);
            bool runHover = Raylib.CheckCollisionPointRec(Raylib.GetMousePosition(), runButton);
            Color runColor = runHover ? Color.LightGray : Color.Gray;

            Raylib.DrawRectangleRec(runButton, runColor);
            Raylib.DrawRectangleLines((int)runButton.X, (int)runButton.Y,
                (int)runButton.Width, (int)runButton.Height, Color.Black);

            string runText = "Run Full Algorithm";
            int runTextWidth = Raylib.MeasureText(runText, 20);
            Raylib.DrawText(runText,
                (int)(runButton.X + runButton.Width / 2 - runTextWidth / 2),
                (int)(runButton.Y + 10),
                20, Color.Black);

            // 重置按钮
            Rectangle resetButton = new Rectangle(
                GridMargin + 2 * (ButtonWidth + ButtonMargin),
                buttonY, ButtonWidth, ButtonHeight);
            bool resetHover = Raylib.CheckCollisionPointRec(Raylib.GetMousePosition(), resetButton);
            Color resetColor = resetHover ? Color.LightGray : Color.Gray;

            Raylib.DrawRectangleRec(resetButton, resetColor);
            Raylib.DrawRectangleLines((int)resetButton.X, (int)resetButton.Y,
                (int)resetButton.Width, (int)resetButton.Height, Color.Black);

            string resetText = "New Grid";
            int resetTextWidth = Raylib.MeasureText(resetText, 20);
            Raylib.DrawText(resetText,
                (int)(resetButton.X + resetButton.Width / 2 - resetTextWidth / 2),
                (int)(resetButton.Y + 10),
                20, Color.Black);

            // 检查按钮点击
            if (Raylib.IsMouseButtonPressed(MouseButton.Left))
            {
                if (stepHover && state != AlgorithmState.Completed)
                {
                    StepAlgorithm();
                }
                else if (runHover)
                {
                    RunFullAlgorithm();
                }
                else if (resetHover)
                {
                    GenerateGrid();
                }
            }
        }

        // 主程序入口
        public static void Main()
        {
            Sweep program = new Sweep();
            program.Run();
        }

        // 运行程序
        private void Run()
        {
            // 初始化网格
            rows = 12;
            cols = 12;
            GenerateGrid();

            // 初始化窗口
            int screenWidth = GridMargin * 2 + cols * CellSize + 400; // 为信息面板留出空间
            int screenHeight = GridMargin * 2 + rows * CellSize + 100; // 为按钮留出空间
            Raylib.InitWindow(screenWidth, screenHeight, "Pure Sweep Algorithm - Maximum Island Area");
            Raylib.SetTargetFPS(60);

            // 主循环
            while (!Raylib.WindowShouldClose())
            {
                // 绘制
                Raylib.BeginDrawing();
                Raylib.ClearBackground(Color.RayWhite);

                DrawGrid();
                DrawInfoPanel();
                DrawControlButtons();

                // 状态提示
                if (state == AlgorithmState.Completed)
                {
                    string completionText = $"Algorithm Completed! Maximum Island Area: {maxIslandArea}";
                    int textWidth = Raylib.MeasureText(completionText, 28);
                    Raylib.DrawText(completionText,
                        (screenWidth - textWidth) / 2,
                        GridMargin + rows * CellSize + 80,
                        28, Color.DarkGreen);
                }

                Raylib.EndDrawing();
            }

            // 关闭窗口
            Raylib.CloseWindow();
        }
    }
}