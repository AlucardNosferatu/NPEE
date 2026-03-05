using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Text;
using Raylib_cs;

namespace SimplifiedGridDemo
{
    public class SimplifiedGrid
    {
        // Program state enumeration
        private enum ProgramState
        {
            InitialGrid,
            RandomEdgeRemoval,
            FindHighDegreeVertices,
            BuildSimplifiedGraph,
            UnionFindMerge,
            Complete
        }

        // Grid dimensions and parameters
        private const int GridSize = 15; // Grid size (number of vertices per side)
        private const int CellSize = 40; // Cell size (pixels)
        private const int Padding = 50; // Canvas margin
        private const float NodeRadius = 8f; // Node drawing radius
        private const float EdgeThickness = 2f; // Edge line width

        // Extended window dimensions for matrix display - WIDER FOR BETTER MATRIX DISPLAY
        private static readonly int MatrixAreaWidth = 500; // Increased from 400 to 500
        private static readonly int WindowWidth = 2 * Padding + GridSize * CellSize + MatrixAreaWidth;
        private static readonly int WindowHeight = 2 * Padding + GridSize * CellSize + 100; // Extra space for buttons

        // Program state
        private static ProgramState currentState = ProgramState.InitialGrid;
        private static Random random = new Random();

        // Grid data structures
        private static bool[,] horizontalEdges; // Horizontal edges (rows × columns+1)
        private static bool[,] verticalEdges;   // Vertical edges (rows+1 × columns)
        private static List<VertexInfo> highDegreeVertices = new List<VertexInfo>(); // High-degree vertices
        private static List<EdgeInfo> simplifiedEdges = new List<EdgeInfo>(); // Edges in simplified graph

        // Union-Find data structures
        private static int[] parent; // Parent array for union-find
        private static int[] rank;   // Rank array for union-find (for optimization)
        private static int[,] filteredReachabilityMatrix; // Filtered reachability matrix (without single-node components)
        private static List<List<int>> connectedComponents = new List<List<int>>(); // Connected components
        private static List<int> filteredVertexIndices = new List<int>(); // Indices of vertices in filtered matrix
        private static Dictionary<int, int> originalToFilteredIndex = new Dictionary<int, int>(); // Map original index to filtered index

        // Button areas
        private static Rectangle stepButton = new Rectangle(WindowWidth / 2 - 150, WindowHeight - 80, 140, 40);
        private static Rectangle resetButton = new Rectangle(WindowWidth / 2 + 10, WindowHeight - 80, 140, 40);

        // Vertex information class
        private class VertexInfo
        {
            public int X { get; set; }
            public int Y { get; set; }
            public int Degree { get; set; }
            public int Index { get; set; } // Index in the highDegreeVertices list

            public VertexInfo(int x, int y, int degree)
            {
                X = x;
                Y = y;
                Degree = degree;
            }
        }

        // Edge information class
        private class EdgeInfo
        {
            public VertexInfo From { get; set; }
            public VertexInfo To { get; set; }

            public EdgeInfo(VertexInfo from, VertexInfo to)
            {
                From = from;
                To = to;
            }
        }

        // Main function
        public static void Main()
        {
            // Initialize window
            Raylib.InitWindow(WindowWidth, WindowHeight, "Grid Simplification Algorithm Demo with Union-Find");
            Raylib.SetTargetFPS(60);

            // Initialize grid edges
            InitializeGrid();

            // Main loop
            while (!Raylib.WindowShouldClose())
            {
                // Handle input
                HandleInput();

                // Begin drawing
                Raylib.BeginDrawing();
                Raylib.ClearBackground(Color.RayWhite);

                // Draw current state
                DrawCurrentState();

                // Draw UI
                DrawUI();

                // End drawing
                Raylib.EndDrawing();
            }

            Raylib.CloseWindow();
        }

        // Initialize grid
        private static void InitializeGrid()
        {
            // Initialize all edges as present
            horizontalEdges = new bool[GridSize, GridSize + 1];
            verticalEdges = new bool[GridSize + 1, GridSize];

            for (int i = 0; i < GridSize; i++)
            {
                for (int j = 0; j < GridSize + 1; j++)
                {
                    horizontalEdges[i, j] = true;
                }
            }

            for (int i = 0; i < GridSize + 1; i++)
            {
                for (int j = 0; j < GridSize; j++)
                {
                    verticalEdges[i, j] = true;
                }
            }

            // Reset state
            currentState = ProgramState.InitialGrid;
            highDegreeVertices.Clear();
            simplifiedEdges.Clear();
            filteredReachabilityMatrix = null;
            connectedComponents.Clear();
            filteredVertexIndices.Clear();
            originalToFilteredIndex.Clear();
        }

        // Handle input
        private static void HandleInput()
        {
            // Check button clicks
            if (Raylib.IsMouseButtonPressed(MouseButton.Left))
            {
                Vector2 mousePos = Raylib.GetMousePosition();

                // Step button
                if (Raylib.CheckCollisionPointRec(mousePos, stepButton))
                {
                    PerformStep();
                }

                // Reset button
                if (Raylib.CheckCollisionPointRec(mousePos, resetButton))
                {
                    InitializeGrid();
                }
            }
        }

        // Perform step operation
        private static void PerformStep()
        {
            switch (currentState)
            {
                case ProgramState.InitialGrid:
                    // Randomly remove some edges
                    RemoveRandomEdges();
                    currentState = ProgramState.RandomEdgeRemoval;
                    break;

                case ProgramState.RandomEdgeRemoval:
                    // Find vertices with degree > 2
                    FindHighDegreeVertices();
                    currentState = ProgramState.FindHighDegreeVertices;
                    break;

                case ProgramState.FindHighDegreeVertices:
                    // Build simplified graph
                    BuildSimplifiedGraph();
                    currentState = ProgramState.BuildSimplifiedGraph;
                    break;

                case ProgramState.BuildSimplifiedGraph:
                    // Perform union-find merge
                    PerformUnionFind();
                    currentState = ProgramState.UnionFindMerge;
                    break;

                case ProgramState.UnionFindMerge:
                    // Complete
                    currentState = ProgramState.Complete;
                    break;

                case ProgramState.Complete:
                    // Restart
                    currentState = ProgramState.InitialGrid;
                    break;
            }
        }

        // Randomly remove some edges - OPTIMIZED VERSION
        private static void RemoveRandomEdges()
        {
            int totalEdges = GridSize * (GridSize + 1) + (GridSize + 1) * GridSize;
            int initialRemovalCount = (int)(0.33f * totalEdges); // First round: remove 50% of edges
            int targetedRemovalCount = (int)(0.25f * totalEdges); // Second round: remove another 25% of edges

            Console.WriteLine($"Total edges: {totalEdges}");
            Console.WriteLine($"First round removal: {initialRemovalCount} edges");
            Console.WriteLine($"Second round removal: {targetedRemovalCount} edges");

            // First round: randomly remove 50% of edges
            for (int i = 0; i < initialRemovalCount; i++)
            {
                if (random.Next(2) == 0)
                {
                    // Remove horizontal edge
                    int row = random.Next(GridSize);
                    int col = random.Next(GridSize + 1);
                    horizontalEdges[row, col] = false;
                }
                else
                {
                    // Remove vertical edge
                    int row = random.Next(GridSize + 1);
                    int col = random.Next(GridSize);
                    verticalEdges[row, col] = false;
                }
            }

            // Second round: prioritize removing edges connected to high-degree vertices
            for (int i = 0; i < targetedRemovalCount; i++)
            {
                // Calculate current degree of all vertices
                int[,] vertexDegrees = CalculateAllVertexDegrees();

                // Collect all edges that still exist
                List<EdgeWithDegreeInfo> edgesWithDegreeInfo = new List<EdgeWithDegreeInfo>();

                // Collect horizontal edges
                for (int y = 0; y < GridSize; y++)
                {
                    for (int x = 0; x <= GridSize; x++)
                    {
                        if (horizontalEdges[y, x])
                        {
                            // Get the two endpoints of the edge
                            int maxDegree = Math.Max(vertexDegrees[x, y], vertexDegrees[x, y + 1]);
                            int priority = maxDegree;

                            edgesWithDegreeInfo.Add(new EdgeWithDegreeInfo
                            {
                                IsHorizontal = true,
                                X = x,
                                Y = y,
                                MaxVertexDegree = maxDegree,
                                Priority = priority
                            });
                        }
                    }
                }

                // Collect vertical edges
                for (int y = 0; y <= GridSize; y++)
                {
                    for (int x = 0; x < GridSize; x++)
                    {
                        if (verticalEdges[y, x])
                        {
                            // Get the two endpoints of the edge
                            int maxDegree = Math.Max(vertexDegrees[x, y], vertexDegrees[x + 1, y]);
                            int priority = maxDegree;

                            edgesWithDegreeInfo.Add(new EdgeWithDegreeInfo
                            {
                                IsHorizontal = false,
                                X = x,
                                Y = y,
                                MaxVertexDegree = maxDegree,
                                Priority = priority
                            });
                        }
                    }
                }

                if (edgesWithDegreeInfo.Count == 0)
                {
                    // No edges left to delete
                    Console.WriteLine($"No edges left to delete at iteration {i}");
                    break;
                }

                // Group edges by priority: prioritize removing edges connected to degree-4 vertices, then degree-3, finally degree-2
                var edgesByPriority = edgesWithDegreeInfo
                    .GroupBy(e => e.Priority)
                    .OrderByDescending(g => g.Key) // Sort from highest to lowest
                    .ToList();

                // Select edge based on priority
                EdgeWithDegreeInfo edgeToRemove = null;
                foreach (var group in edgesByPriority)
                {
                    if (group.Any())
                    {
                        // Randomly select an edge from the current priority group
                        edgeToRemove = group.ElementAt(random.Next(group.Count()));
                        break;
                    }
                }

                if (edgeToRemove != null)
                {
                    // Remove the selected edge
                    if (edgeToRemove.IsHorizontal)
                    {
                        horizontalEdges[edgeToRemove.Y, edgeToRemove.X] = false;
                    }
                    else
                    {
                        verticalEdges[edgeToRemove.Y, edgeToRemove.X] = false;
                    }
                }
            }

            // Ensure the grid still has at least one connected component
            EnsureConnectivity();

            // Calculate final degree distribution
            int[,] finalDegrees = CalculateAllVertexDegrees();
            CountDegreeDistribution(finalDegrees);
        }

        // Calculate degree of all vertices
        private static int[,] CalculateAllVertexDegrees()
        {
            int[,] degrees = new int[GridSize + 1, GridSize + 1];

            for (int x = 0; x <= GridSize; x++)
            {
                for (int y = 0; y <= GridSize; y++)
                {
                    degrees[x, y] = CalculateVertexDegree(x, y);
                }
            }

            return degrees;
        }

        // Count degree distribution
        private static void CountDegreeDistribution(int[,] degrees)
        {
            int[] distribution = new int[5]; // Degrees 0-4

            for (int x = 0; x <= GridSize; x++)
            {
                for (int y = 0; y <= GridSize; y++)
                {
                    int degree = degrees[x, y];
                    if (degree >= 0 && degree <= 4)
                    {
                        distribution[degree]++;
                    }
                }
            }

            Console.WriteLine("Final vertex degree distribution:");
            for (int i = 0; i <= 4; i++)
            {
                Console.WriteLine($"  Degree {i}: {distribution[i]} vertices");
            }

            // Calculate high-degree vertex ratio
            int highDegreeVertices = distribution[3] + distribution[4];
            int totalVertices = (GridSize + 1) * (GridSize + 1);
            float highDegreeRatio = (float)highDegreeVertices / totalVertices;
            Console.WriteLine($"High-degree vertices (3+): {highDegreeVertices} out of {totalVertices} ({highDegreeRatio:P})");
        }

        // Ensure at least one connected component exists
        private static void EnsureConnectivity()
        {
            // Use BFS to check connectivity
            bool[,] visited = new bool[GridSize + 1, GridSize + 1];
            int connectedComponents = 0;

            for (int x = 0; x <= GridSize; x++)
            {
                for (int y = 0; y <= GridSize; y++)
                {
                    if (!visited[x, y])
                    {
                        // Start BFS from this vertex
                        Queue<(int, int)> queue = new Queue<(int, int)>();
                        queue.Enqueue((x, y));
                        visited[x, y] = true;

                        while (queue.Count > 0)
                        {
                            var (cx, cy) = queue.Dequeue();

                            // Check edges in four directions
                            // Up
                            if (cy > 0 && horizontalEdges[cy - 1, cx] && !visited[cx, cy - 1])
                            {
                                queue.Enqueue((cx, cy - 1));
                                visited[cx, cy - 1] = true;
                            }

                            // Down
                            if (cy < GridSize && horizontalEdges[cy, cx] && !visited[cx, cy + 1])
                            {
                                queue.Enqueue((cx, cy + 1));
                                visited[cx, cy + 1] = true;
                            }

                            // Left
                            if (cx > 0 && verticalEdges[cy, cx - 1] && !visited[cx - 1, cy])
                            {
                                queue.Enqueue((cx - 1, cy));
                                visited[cx - 1, cy] = true;
                            }

                            // Right
                            if (cx < GridSize && verticalEdges[cy, cx] && !visited[cx + 1, cy])
                            {
                                queue.Enqueue((cx + 1, cy));
                                visited[cx + 1, cy] = true;
                            }
                        }

                        connectedComponents++;
                    }
                }
            }

            // If no connected components, restore some edges
            if (connectedComponents == 0)
            {
                // Simply restore some edges to ensure connectivity
                for (int i = 0; i < GridSize; i++)
                {
                    horizontalEdges[i, 0] = true;
                    verticalEdges[0, i] = true;
                }
            }
        }

        // Find vertices with degree > 2
        private static void FindHighDegreeVertices()
        {
            highDegreeVertices.Clear();

            for (int x = 0; x <= GridSize; x++)
            {
                for (int y = 0; y <= GridSize; y++)
                {
                    int degree = CalculateVertexDegree(x, y);

                    if (degree > 2)
                    {
                        highDegreeVertices.Add(new VertexInfo(x, y, degree));
                    }
                }
            }

            // Assign indices to vertices for union-find
            for (int i = 0; i < highDegreeVertices.Count; i++)
            {
                highDegreeVertices[i].Index = i;
            }
        }

        // Calculate vertex degree
        private static int CalculateVertexDegree(int x, int y)
        {
            int degree = 0;

            // Check edges in four directions
            // Up
            if (y > 0 && horizontalEdges[y - 1, x])
                degree++;

            // Down
            if (y < GridSize && horizontalEdges[y, x])
                degree++;

            // Left
            if (x > 0 && verticalEdges[y, x - 1])
                degree++;

            // Right
            if (x < GridSize && verticalEdges[y, x])
                degree++;

            return degree;
        }

        // Build simplified graph
        private static void BuildSimplifiedGraph()
        {
            simplifiedEdges.Clear();

            // For each high-degree vertex, find all other high-degree vertices
            // that are directly connected by a path with no intermediate high-degree vertices
            for (int i = 0; i < highDegreeVertices.Count; i++)
            {
                for (int j = i + 1; j < highDegreeVertices.Count; j++)
                {
                    if (AreVerticesDirectlyConnected(highDegreeVertices[i], highDegreeVertices[j]))
                    {
                        simplifiedEdges.Add(new EdgeInfo(highDegreeVertices[i], highDegreeVertices[j]));
                    }
                }
            }
        }

        // Check if two vertices are directly connected (with no intermediate high-degree vertices)
        private static bool AreVerticesDirectlyConnected(VertexInfo v1, VertexInfo v2)
        {
            // First check if they are in the same connected component
            if (!AreVerticesConnected(v1, v2))
            {
                return false;
            }

            // Now check if there's a path between them that doesn't pass through
            // any other high-degree vertices
            return FindDirectPath(v1, v2);
        }

        // Find if there's a direct path between two vertices (no intermediate high-degree vertices)
        private static bool FindDirectPath(VertexInfo v1, VertexInfo v2)
        {
            // Use BFS to find a path
            Queue<(int, int, List<(int, int)>)> queue = new Queue<(int, int, List<(int, int)>)>();
            bool[,] visited = new bool[GridSize + 1, GridSize + 1];

            // Start BFS from v1
            queue.Enqueue((v1.X, v1.Y, new List<(int, int)>()));
            visited[v1.X, v1.Y] = true;

            while (queue.Count > 0)
            {
                var (x, y, path) = queue.Dequeue();

                // If we reached v2
                if (x == v2.X && y == v2.Y)
                {
                    // Check if the path contains any other high-degree vertices (excluding start and end)
                    foreach (var (px, py) in path)
                    {
                        // Skip the start and end points
                        if ((px == v1.X && py == v1.Y) || (px == v2.X && py == v2.Y))
                            continue;

                        // Check if this point is a high-degree vertex
                        if (highDegreeVertices.Any(v => v.X == px && v.Y == py))
                        {
                            return false; // Path contains another high-degree vertex
                        }
                    }
                    return true; // Found a direct path
                }

                // Check all four directions
                List<(int, int, int, int)> directions = new List<(int, int, int, int)>
                {
                    (0, -1, y, x), // Up: check horizontal edge above
                    (0, 1, y, x),  // Down: check horizontal edge at current position
                    (-1, 0, y, x - 1), // Left: check vertical edge to the left
                    (1, 0, y, x)   // Right: check vertical edge at current position
                };

                foreach (var (dx, dy, checkY, checkX) in directions)
                {
                    int newX = x + dx;
                    int newY = y + dy;

                    // Check bounds
                    if (newX < 0 || newX > GridSize || newY < 0 || newY > GridSize)
                        continue;

                    // Check if we can move in this direction
                    bool canMove = false;
                    if (dx == 0 && dy == -1) // Moving up
                    {
                        canMove = checkY > 0 && horizontalEdges[checkY - 1, checkX];
                    }
                    else if (dx == 0 && dy == 1) // Moving down
                    {
                        canMove = checkY < GridSize && horizontalEdges[checkY, checkX];
                    }
                    else if (dx == -1 && dy == 0) // Moving left
                    {
                        canMove = checkX > 0 && verticalEdges[checkY, checkX - 1];
                    }
                    else if (dx == 1 && dy == 0) // Moving right
                    {
                        canMove = checkX < GridSize && verticalEdges[checkY, checkX];
                    }

                    if (canMove && !visited[newX, newY])
                    {
                        // Create a new path with the current point added
                        var newPath = new List<(int, int)>(path);
                        newPath.Add((x, y)); // Add current point to path
                        queue.Enqueue((newX, newY, newPath));
                        visited[newX, newY] = true;
                    }
                }
            }

            return false; // No direct path found
        }

        // Check if two vertices are connected (BFS)
        private static bool AreVerticesConnected(VertexInfo v1, VertexInfo v2)
        {
            // Simple BFS to check connectivity
            bool[,] visited = new bool[GridSize + 1, GridSize + 1];
            Queue<(int, int)> queue = new Queue<(int, int)>();

            queue.Enqueue((v1.X, v1.Y));
            visited[v1.X, v1.Y] = true;

            while (queue.Count > 0)
            {
                var (x, y) = queue.Dequeue();

                // If we reached the target vertex
                if (x == v2.X && y == v2.Y)
                {
                    return true;
                }

                // Check edges in four directions
                // Up
                if (y > 0 && horizontalEdges[y - 1, x] && !visited[x, y - 1])
                {
                    queue.Enqueue((x, y - 1));
                    visited[x, y - 1] = true;
                }

                // Down
                if (y < GridSize && horizontalEdges[y, x] && !visited[x, y + 1])
                {
                    queue.Enqueue((x, y + 1));
                    visited[x, y + 1] = true;
                }

                // Left
                if (x > 0 && verticalEdges[y, x - 1] && !visited[x - 1, y])
                {
                    queue.Enqueue((x - 1, y));
                    visited[x - 1, y] = true;
                }

                // Right
                if (x < GridSize && verticalEdges[y, x] && !visited[x + 1, y])
                {
                    queue.Enqueue((x + 1, y));
                    visited[x + 1, y] = true;
                }
            }

            return false;
        }

        // Perform Union-Find merge on simplified graph
        private static void PerformUnionFind()
        {
            int n = highDegreeVertices.Count;

            // Initialize union-find structures
            parent = new int[n];
            rank = new int[n];

            for (int i = 0; i < n; i++)
            {
                parent[i] = i; // Each node is its own parent initially
                rank[i] = 0;
            }

            // Merge connected vertices (edges in simplified graph)
            foreach (var edge in simplifiedEdges)
            {
                Union(edge.From.Index, edge.To.Index);
            }

            // Find connected components
            connectedComponents.Clear();
            Dictionary<int, List<int>> componentMap = new Dictionary<int, List<int>>();

            for (int i = 0; i < n; i++)
            {
                int root = Find(i);
                if (!componentMap.ContainsKey(root))
                {
                    componentMap[root] = new List<int>();
                }
                componentMap[root].Add(i);
            }

            foreach (var component in componentMap.Values)
            {
                connectedComponents.Add(component);
            }

            // Filter out components with only 1 node (size == 1)
            filteredVertexIndices.Clear();
            originalToFilteredIndex.Clear();

            foreach (var component in connectedComponents)
            {
                if (component.Count > 1)
                {
                    foreach (var vertexIndex in component)
                    {
                        filteredVertexIndices.Add(vertexIndex);
                    }
                }
            }

            // Sort filtered indices for consistent display
            filteredVertexIndices.Sort();

            // Create mapping from original index to filtered index
            for (int i = 0; i < filteredVertexIndices.Count; i++)
            {
                originalToFilteredIndex[filteredVertexIndices[i]] = i;
            }

            // Generate filtered reachability matrix
            if (filteredVertexIndices.Count > 0)
            {
                int filteredCount = filteredVertexIndices.Count;
                filteredReachabilityMatrix = new int[filteredCount, filteredCount];

                for (int i = 0; i < filteredCount; i++)
                {
                    for (int j = 0; j < filteredCount; j++)
                    {
                        int originalI = filteredVertexIndices[i];
                        int originalJ = filteredVertexIndices[j];
                        filteredReachabilityMatrix[i, j] = Find(originalI) == Find(originalJ) ? 1 : 0;
                    }
                }
            }
            else
            {
                filteredReachabilityMatrix = new int[0, 0];
            }

            Console.WriteLine($"Filtered reachability matrix: {filteredVertexIndices.Count} vertices (removed {n - filteredVertexIndices.Count} isolated vertices)");
        }

        // Find operation for union-find (with path compression)
        private static int Find(int x)
        {
            if (parent[x] != x)
            {
                parent[x] = Find(parent[x]); // Path compression
            }
            return parent[x];
        }

        // Union operation for union-find (with union by rank)
        private static void Union(int x, int y)
        {
            int rootX = Find(x);
            int rootY = Find(y);

            if (rootX != rootY)
            {
                // Union by rank
                if (rank[rootX] < rank[rootY])
                {
                    parent[rootX] = rootY;
                }
                else if (rank[rootX] > rank[rootY])
                {
                    parent[rootY] = rootX;
                }
                else
                {
                    parent[rootY] = rootX;
                    rank[rootX]++;
                }
            }
        }

        // Draw current state
        private static void DrawCurrentState()
        {
            // Draw grid edges
            DrawGridEdges();

            // Draw different content based on state
            switch (currentState)
            {
                case ProgramState.InitialGrid:
                    DrawInitialGridInfo();
                    break;

                case ProgramState.RandomEdgeRemoval:
                    DrawRandomEdgeRemovalInfo();
                    break;

                case ProgramState.FindHighDegreeVertices:
                    DrawHighDegreeVertices();
                    DrawFindVerticesInfo();
                    break;

                case ProgramState.BuildSimplifiedGraph:
                    DrawHighDegreeVertices();
                    DrawSimplifiedGraph();
                    DrawSimplifiedGraphInfo();
                    break;

                case ProgramState.UnionFindMerge:
                    DrawHighDegreeVertices();
                    DrawSimplifiedGraph();
                    DrawUnionFindInfo();
                    break;

                case ProgramState.Complete:
                    DrawHighDegreeVertices();
                    DrawSimplifiedGraph();
                    DrawCompleteInfo();
                    break;
            }
        }

        // Draw grid edges
        private static void DrawGridEdges()
        {
            // Draw horizontal edges
            for (int y = 0; y < GridSize; y++)
            {
                for (int x = 0; x <= GridSize; x++)
                {
                    if (horizontalEdges[y, x])
                    {
                        int startX = Padding + x * CellSize;
                        int startY = Padding + y * CellSize;
                        int endX = Padding + x * CellSize;
                        int endY = Padding + (y + 1) * CellSize;

                        Raylib.DrawLine(startX, startY, endX, endY, Color.Gray);
                    }
                }
            }

            // Draw vertical edges
            for (int y = 0; y <= GridSize; y++)
            {
                for (int x = 0; x < GridSize; x++)
                {
                    if (verticalEdges[y, x])
                    {
                        int startX = Padding + x * CellSize;
                        int startY = Padding + y * CellSize;
                        int endX = Padding + (x + 1) * CellSize;
                        int endY = Padding + y * CellSize;

                        Raylib.DrawLine(startX, startY, endX, endY, Color.Gray);
                    }
                }
            }

            // Draw grid vertices
            for (int x = 0; x <= GridSize; x++)
            {
                for (int y = 0; y <= GridSize; y++)
                {
                    int posX = Padding + x * CellSize;
                    int posY = Padding + y * CellSize;
                    Raylib.DrawCircle(posX, posY, 2, Color.DarkGray);
                }
            }
        }

        // Draw high-degree vertices
        private static void DrawHighDegreeVertices()
        {
            // Assign colors to connected components for visual distinction
            Color[] componentColors = new Color[]
            {
                Color.Red, Color.Blue, Color.Green, Color.Purple,
                Color.Orange, Color.Pink, Color.SkyBlue, Color.Lime,
                Color.Gold, Color.Violet, Color.Brown, Color.Beige
            };

            // Draw each vertex with its component color
            for (int i = 0; i < highDegreeVertices.Count; i++)
            {
                var vertex = highDegreeVertices[i];
                int posX = Padding + vertex.X * CellSize;
                int posY = Padding + vertex.Y * CellSize;

                // Determine component color (only in UnionFind and Complete states)
                Color vertexColor = Color.Red;
                if (currentState == ProgramState.UnionFindMerge || currentState == ProgramState.Complete)
                {
                    int root = Find(i);
                    int componentIndex = connectedComponents.FindIndex(comp => comp.Contains(i));
                    if (componentIndex >= 0 && componentIndex < componentColors.Length)
                    {
                        vertexColor = componentColors[componentIndex % componentColors.Length];
                    }
                }

                // Draw node
                Raylib.DrawCircle(posX, posY, NodeRadius, vertexColor);

                // Draw node index (for matrix reference)
                Raylib.DrawText(i.ToString(), posX - 5, posY - 20, 12, Color.Black);

                // Mark isolated vertices (in components of size 1) with a special marker
                if ((currentState == ProgramState.UnionFindMerge || currentState == ProgramState.Complete) &&
                    connectedComponents.Any(comp => comp.Contains(i) && comp.Count == 1))
                {
                    Raylib.DrawCircleLines(posX, posY, NodeRadius + 2, Color.Black);
                    Raylib.DrawText("X", posX - 4, posY - 8, 12, Color.Black);
                }
            }
        }

        // Draw simplified graph
        private static void DrawSimplifiedGraph()
        {
            foreach (var edge in simplifiedEdges)
            {
                int fromX = Padding + edge.From.X * CellSize;
                int fromY = Padding + edge.From.Y * CellSize;
                int toX = Padding + edge.To.X * CellSize;
                int toY = Padding + edge.To.Y * CellSize;

                // Draw simplified graph edges
                Raylib.DrawLineEx(
                    new Vector2(fromX, fromY),
                    new Vector2(toX, toY),
                    EdgeThickness * 2,
                    Color.Blue
                );
            }
        }

        // Draw UI
        private static void DrawUI()
        {
            // Draw state text
            string stateText = GetStateText();
            Raylib.DrawText(stateText, 20, 20, 20, Color.DarkBlue);

            // Draw buttons
            DrawButton(stepButton, "Next Step", currentState == ProgramState.Complete ? Color.Green : Color.Blue);
            DrawButton(resetButton, "Reset", Color.Orange);

            // Draw instruction text
            Raylib.DrawText("Grid Simplification Algorithm Demo with Union-Find", WindowWidth / 2 - 200, WindowHeight - 120, 20, Color.DarkBlue);

            // Draw grid statistics
            DrawGridStats();

            // Draw matrix area if we have reachability matrix
            if (filteredReachabilityMatrix != null && filteredVertexIndices.Count > 0)
            {
                DrawMatrixArea();
            }
            else if (filteredReachabilityMatrix != null && filteredVertexIndices.Count == 0)
            {
                // No vertices in filtered matrix (all are isolated)
                DrawNoMatrixMessage();
            }
        }

        // Get state text
        private static string GetStateText()
        {
            switch (currentState)
            {
                case ProgramState.InitialGrid:
                    return "Step 1: Initial Complete Grid";
                case ProgramState.RandomEdgeRemoval:
                    return "Step 2: Optimized Edge Removal for More 2-Degree Vertices";
                case ProgramState.FindHighDegreeVertices:
                    return $"Step 3: Found {highDegreeVertices.Count} Vertices with Degree > 2";
                case ProgramState.BuildSimplifiedGraph:
                    return $"Step 4: Build Simplified Graph ({simplifiedEdges.Count} edges)";
                case ProgramState.UnionFindMerge:
                    return $"Step 5: Union-Find Merge ({connectedComponents.Count} connected components)";
                case ProgramState.Complete:
                    return "Complete: Filtered Reachability Matrix Generated";
                default:
                    return "Unknown State";
            }
        }

        // Draw button
        private static void DrawButton(Rectangle rect, string text, Color color)
        {
            // Draw button background
            Raylib.DrawRectangleRec(rect, color);

            // Draw button border
            Raylib.DrawRectangleLinesEx(rect, 2, Color.DarkGray);

            // Draw button text
            int textWidth = Raylib.MeasureText(text, 20);
            int textX = (int)(rect.X + rect.Width / 2 - textWidth / 2);
            int textY = (int)(rect.Y + rect.Height / 2 - 10);
            Raylib.DrawText(text, textX, textY, 20, Color.White);
        }

        // Draw grid statistics
        private static void DrawGridStats()
        {
            int totalVertices = (GridSize + 1) * (GridSize + 1);
            int remainingHorizontalEdges = 0;
            int remainingVerticalEdges = 0;

            // Count remaining edges
            for (int i = 0; i < GridSize; i++)
            {
                for (int j = 0; j < GridSize + 1; j++)
                {
                    if (horizontalEdges[i, j]) remainingHorizontalEdges++;
                }
            }

            for (int i = 0; i < GridSize + 1; i++)
            {
                for (int j = 0; j < GridSize; j++)
                {
                    if (verticalEdges[i, j]) remainingVerticalEdges++;
                }
            }

            string stats = $"Vertices: {totalVertices} | Edges: {remainingHorizontalEdges + remainingVerticalEdges} | High-degree Vertices: {highDegreeVertices.Count}";
            Raylib.DrawText(stats, WindowWidth - Raylib.MeasureText(stats, 16) - 20, 20, 16, Color.DarkGray);

            // Add degree distribution info if available
            if (highDegreeVertices.Count > 0)
            {
                int[,] degrees = CalculateAllVertexDegrees();
                int twoDegreeCount = 0;
                int highDegreeCount = 0;

                for (int x = 0; x <= GridSize; x++)
                {
                    for (int y = 0; y <= GridSize; y++)
                    {
                        int degree = degrees[x, y];
                        if (degree == 2) twoDegreeCount++;
                        if (degree > 2) highDegreeCount++;
                    }
                }

                string degreeStats = $"2-degree: {twoDegreeCount} | High-degree: {highDegreeCount} | Ratio: {(float)highDegreeCount / totalVertices:P}";
                Raylib.DrawText(degreeStats, WindowWidth - Raylib.MeasureText(degreeStats, 14) - 20, 40, 14, Color.DarkGray);
            }
        }

        // Draw matrix area on the right side - COMPACT VERSION
        private static void DrawMatrixArea()
        {
            int matrixStartX = Padding + GridSize * CellSize + 20;
            int matrixStartY = Padding + 40;
            int n = filteredVertexIndices.Count;

            // Calculate compact cell size based on available space
            int maxMatrixHeight = WindowHeight - matrixStartY - 100; // Leave space at bottom
            int maxMatrixWidth = MatrixAreaWidth - 40; // Leave some margin

            // Calculate cell size to fit the matrix in available space
            int cellSize = Math.Min(20, Math.Min(maxMatrixWidth / (n + 1), maxMatrixHeight / (n + 1)));
            cellSize = Math.Max(12, cellSize); // Minimum cell size

            // If matrix is still too big, reduce cell size further
            if (n * cellSize > maxMatrixWidth || n * cellSize > maxMatrixHeight)
            {
                cellSize = Math.Min(10, Math.Min(maxMatrixWidth / n, maxMatrixHeight / n));
                cellSize = Math.Max(8, cellSize); // Absolute minimum
            }

            // Draw matrix background
            Raylib.DrawRectangle(matrixStartX - 10, matrixStartY - 30,
                n * cellSize + 50, n * cellSize + 80, new Color(240, 240, 240, 255));

            // Draw title
            Raylib.DrawText("Filtered Reachability Matrix", matrixStartX, matrixStartY - 25, 18, Color.DarkBlue);

            // Draw component count and filtering info
            if (connectedComponents.Count > 0)
            {
                int multiNodeComponents = connectedComponents.Count(c => c.Count > 1);
                int isolatedNodes = connectedComponents.Count(c => c.Count == 1);

                Raylib.DrawText($"Components (>1): {multiNodeComponents}, Isolated: {isolatedNodes}",
                    matrixStartX, matrixStartY, 14, Color.DarkGreen);

                Raylib.DrawText($"Matrix: {n}×{n} (original: {highDegreeVertices.Count}×{highDegreeVertices.Count})",
                    matrixStartX, matrixStartY + 16, 14, Color.DarkGray);
            }

            // Draw matrix headers (row and column indices - show original indices)
            int matrixContentStartY = matrixStartY + 40;

            // Draw column headers
            for (int i = 0; i < n; i++)
            {
                int originalIndex = filteredVertexIndices[i];
                string indexText = originalIndex.ToString();
                int fontSize = cellSize > 14 ? 10 : 8;
                int textWidth = Raylib.MeasureText(indexText, fontSize);
                Raylib.DrawText(indexText,
                    matrixStartX + i * cellSize + (cellSize - textWidth) / 2,
                    matrixContentStartY - 20,
                    fontSize, Color.Black);
            }

            // Draw row headers and matrix cells
            for (int i = 0; i < n; i++)
            {
                int originalIndex = filteredVertexIndices[i];
                string indexText = originalIndex.ToString();
                int fontSize = cellSize > 14 ? 10 : 8;
                int textWidth = Raylib.MeasureText(indexText, fontSize);

                // Draw row header
                Raylib.DrawText(indexText,
                    matrixStartX - textWidth - 5,
                    matrixContentStartY + i * cellSize + (cellSize - fontSize) / 2,
                    fontSize, Color.Black);

                // Draw matrix cells for this row
                for (int j = 0; j < n; j++)
                {
                    int cellX = matrixStartX + j * cellSize;
                    int cellY = matrixContentStartY + i * cellSize;

                    // Draw cell background
                    Color cellColor = filteredReachabilityMatrix[i, j] == 1 ?
                        new Color(100, 200, 100, 220) : // Green for reachable
                        new Color(200, 100, 100, 220);  // Red for unreachable

                    Raylib.DrawRectangle(cellX, cellY, cellSize, cellSize, cellColor);

                    // Draw cell border (thinner for small cells)
                    int borderWidth = cellSize > 15 ? 1 : 0;
                    if (borderWidth > 0)
                    {
                        Raylib.DrawRectangleLines(cellX, cellY, cellSize, cellSize, new Color(80, 80, 80, 255));
                    }

                    // Draw value (only if cell is large enough)
                    if (cellSize >= 12)
                    {
                        string value = filteredReachabilityMatrix[i, j].ToString();
                        int valueFontSize = cellSize > 16 ? 12 : 10;
                        int valueWidth = Raylib.MeasureText(value, valueFontSize);
                        Raylib.DrawText(value,
                            cellX + (cellSize - valueWidth) / 2,
                            cellY + (cellSize - valueFontSize) / 2,
                            valueFontSize, Color.Black);
                    }
                }
            }

            // Draw matrix legend at the bottom
            int legendY = matrixContentStartY + n * cellSize + 10;
            Raylib.DrawText("Legend: ", matrixStartX, legendY, 14, Color.DarkBlue);

            // Draw colored squares for legend
            int legendSquareSize = 12;
            Raylib.DrawRectangle(matrixStartX + 60, legendY + 2, legendSquareSize, legendSquareSize, new Color(100, 200, 100, 220));
            Raylib.DrawText("= 1 (Reachable)", matrixStartX + 75, legendY, 12, Color.DarkGray);

            Raylib.DrawRectangle(matrixStartX + 180, legendY + 2, legendSquareSize, legendSquareSize, new Color(200, 100, 100, 220));
            Raylib.DrawText("= 0 (Not Reachable)", matrixStartX + 195, legendY, 12, Color.DarkGray);

            // Draw note about filtered matrix
            Raylib.DrawText("Note: Shows only vertices in multi-node components",
                matrixStartX, legendY + 20, 10, Color.DarkGray);

            // If matrix is small enough, show connectivity pattern
            if (n <= 15)
            {
                Raylib.DrawText($"Connectivity pattern shown ({n} vertices)",
                    matrixStartX, legendY + 35, 10, Color.DarkBlue);
            }
            else
            {
                Raylib.DrawText($"Large matrix ({n} vertices) - showing compact view",
                    matrixStartX, legendY + 35, 10, Color.DarkBlue);
            }
        }

        // Draw message when no vertices in filtered matrix
        private static void DrawNoMatrixMessage()
        {
            int matrixStartX = Padding + GridSize * CellSize + 20;
            int matrixStartY = Padding + 40;

            // Draw message background
            Raylib.DrawRectangle(matrixStartX - 10, matrixStartY - 30,
                380, 150, new Color(240, 240, 240, 255));

            // Draw title
            Raylib.DrawText("No Filtered Reachability Matrix", matrixStartX, matrixStartY - 25, 18, Color.DarkBlue);

            // Draw message
            Raylib.DrawText("All high-degree vertices are isolated", matrixStartX, matrixStartY + 10, 16, Color.DarkGreen);
            Raylib.DrawText("(each in its own component of size 1)", matrixStartX, matrixStartY + 30, 16, Color.DarkGreen);

            Raylib.DrawText($"Total high-degree vertices: {highDegreeVertices.Count}", matrixStartX, matrixStartY + 60, 14, Color.DarkGray);
            Raylib.DrawText("Connected components: 0 (all isolated)", matrixStartX, matrixStartY + 80, 14, Color.DarkGray);

            Raylib.DrawText("This means the simplified graph", matrixStartX, matrixStartY + 110, 14, Color.DarkGray);
            Raylib.DrawText("has no edges connecting vertices", matrixStartX, matrixStartY + 128, 14, Color.DarkGray);
        }

        // Draw initial grid information
        private static void DrawInitialGridInfo()
        {
            string info = "Complete grid, all edges exist, each vertex has degree 4";
            Raylib.DrawText(info, 20, 50, 16, Color.DarkGreen);
        }

        // Draw random edge removal information
        private static void DrawRandomEdgeRemovalInfo()
        {
            string info = "Two-step edge removal: 1) Random 50% removal 2) Targeted removal (prioritizing high-degree vertices)";
            Raylib.DrawText(info, 20, 50, 16, Color.DarkGreen);
            string goal = "Goal: Create more 2-degree vertices, fewer high-degree branching vertices";
            Raylib.DrawText(goal, 20, 70, 16, Color.DarkGreen);
        }

        // Draw found vertices information
        private static void DrawFindVerticesInfo()
        {
            string info = "Red nodes represent vertices with degree > 2, these are key nodes";
            Raylib.DrawText(info, 20, 50, 16, Color.DarkGreen);

            // Explain benefits of simplified graph
            string benefit = "Simplified graph reduces vertex count, highlights key connectivity";
            Raylib.DrawText(benefit, 20, 70, 16, Color.DarkGreen);
        }

        // Draw simplified graph information
        private static void DrawSimplifiedGraphInfo()
        {
            string info = "Blue lines connect key nodes that are directly connected (no intermediate high-degree nodes)";
            Raylib.DrawText(info, 20, 50, 16, Color.DarkGreen);

            string comparison = $"Original: {(GridSize + 1) * (GridSize + 1)} vertices | Simplified: {highDegreeVertices.Count} vertices, {simplifiedEdges.Count} edges";
            Raylib.DrawText(comparison, 20, 70, 16, Color.DarkGreen);
        }

        // Draw union-find information
        private static void DrawUnionFindInfo()
        {
            string info = "Union-Find algorithm merges connected nodes into components";
            Raylib.DrawText(info, 20, 50, 16, Color.DarkGreen);

            string components = $"Found {connectedComponents.Count} connected components in simplified graph";
            Raylib.DrawText(components, 20, 70, 16, Color.DarkGreen);

            int multiNodeComponents = connectedComponents.Count(c => c.Count > 1);
            string filtered = $"{multiNodeComponents} components have >1 node (will be shown in matrix)";
            Raylib.DrawText(filtered, 20, 90, 16, Color.DarkGreen);
        }

        // Draw completion information
        private static void DrawCompleteInfo()
        {
            string info = "Algorithm demonstration complete! Filtered reachability matrix shows connectivity.";
            Raylib.DrawText(info, 20, 50, 16, Color.DarkGreen);

            string filteredInfo = $"Matrix shows {filteredVertexIndices.Count} vertices (filtered out {highDegreeVertices.Count - filteredVertexIndices.Count} isolated vertices)";
            Raylib.DrawText(filteredInfo, 20, 70, 16, Color.DarkGreen);

            string reset = "Click Reset to restart or Next Step to return to initial grid.";
            Raylib.DrawText(reset, 20, 90, 16, Color.DarkGreen);
        }

        // Helper class: edge with degree information
        private class EdgeWithDegreeInfo
        {
            public bool IsHorizontal { get; set; }
            public int X { get; set; }
            public int Y { get; set; }
            public int MaxVertexDegree { get; set; }
            public int Priority { get; set; }
        }
    }
}