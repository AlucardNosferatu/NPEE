// Toposort.cs - Raylib-CS Topological Sort Demo with LCS
using System;
using System.Collections.Generic;
using System.Numerics;
using System.Text;
using Raylib_cs;

public class Node
{
    public int Id { get; set; }
    public Vector2 Position { get; set; }
    public string Name { get; set; }
    public float Radius { get; set; } = 30f;
    public bool IsSelected { get; set; }
    public bool IsProcessing { get; set; }
    public bool IsProcessed { get; set; }
    public int InDegree { get; set; }
    public List<int> OutgoingEdges { get; set; } = new List<int>();

    // LCS-specific properties
    public string Label { get; set; } = "";
    public string Value { get; set; } = "";
    public int I { get; set; } = -1;
    public int J { get; set; } = -1;

    public Rectangle GetBounds()
    {
        return new Rectangle(Position.X - Radius, Position.Y - Radius, Radius * 2, Radius * 2);
    }

    public bool Contains(Vector2 point)
    {
        return Vector2.Distance(Position, point) <= Radius;
    }
}

public class Edge
{
    public int From { get; set; }
    public int To { get; set; }
    public bool IsHighlighted { get; set; }
}

public class LCSProblem
{
    public string SequenceA { get; set; } = "";
    public string SequenceB { get; set; } = "";
    public int[,] DP { get; set; }
    public string LCS { get; set; } = "";
    public List<string> States { get; set; } = new List<string>();
    public List<string> Transitions { get; set; } = new List<string>();
    public List<int> TopologicalOrder { get; set; } = new List<int>();
    public List<int> DPOrder { get; set; } = new List<int>();
}

public class ToposortDemo
{
    private List<Node> nodes = new List<Node>();
    private List<Edge> edges = new List<Edge>();

    // Algorithm state
    private List<int> sortedNodes = new List<int>();
    private List<int> zeroInDegreeNodes = new List<int>();
    private Queue<int> processingQueue = new Queue<int>();
    private Dictionary<int, int> inDegreeCopy = new Dictionary<int, int>();
    private bool algorithmRunning = false;
    private bool algorithmFinished = false;
    private int currentStep = 0;

    // LCS state
    private LCSProblem lcsProblem = new LCSProblem();
    private bool lcsMode = false;
    private bool lcsGenerated = false;
    private bool lcsSolving = false;
    private int currentDPState = -1;
    private int dpStep = 0;

    // UI state
    private int nextNodeId = 1;
    private int? selectedNode = null;
    private bool isConnecting = false;
    private Vector2? connectionStart = null;
    private Mode currentMode = Mode.AddNode;
    private bool showHelp = true;

    // Color definitions
    private Color nodeColor = new Color(100, 149, 237, 255); // Cornflower blue
    private Color selectedColor = new Color(255, 215, 0, 255); // Gold
    private Color processingColor = new Color(50, 205, 50, 255); // Lime green
    private Color processedColor = new Color(186, 85, 211, 255); // Medium orchid
    private Color edgeColor = new Color(169, 169, 169, 255); // Dark gray
    private Color highlightedEdgeColor = new Color(220, 20, 60, 255); // Crimson
    private Color lcsNodeColor = new Color(70, 130, 180, 255); // Steel blue
    private Color lcsHighlightColor = new Color(255, 140, 0, 255); // Dark orange

    private enum Mode
    {
        AddNode,
        ConnectNodes,
        DeleteNode,
        DeleteEdge
    }

    public void Initialize()
    {
        // Create example DAG
        CreateExampleGraph();
    }

    private void CreateExampleGraph()
    {
        // Clear existing graph
        nodes.Clear();
        edges.Clear();
        nextNodeId = 1;

        // Create nodes
        var node1 = new Node { Id = nextNodeId++, Position = new Vector2(400, 150), Name = "A" };
        var node2 = new Node { Id = nextNodeId++, Position = new Vector2(300, 250), Name = "B" };
        var node3 = new Node { Id = nextNodeId++, Position = new Vector2(500, 250), Name = "C" };
        var node4 = new Node { Id = nextNodeId++, Position = new Vector2(200, 350), Name = "D" };
        var node5 = new Node { Id = nextNodeId++, Position = new Vector2(400, 350), Name = "E" };
        var node6 = new Node { Id = nextNodeId++, Position = new Vector2(600, 350), Name = "F" };
        var node7 = new Node { Id = nextNodeId++, Position = new Vector2(400, 450), Name = "G" };

        nodes.AddRange(new[] { node1, node2, node3, node4, node5, node6, node7 });

        // Create edges
        AddEdge(node1.Id, node2.Id);
        AddEdge(node1.Id, node3.Id);
        AddEdge(node2.Id, node4.Id);
        AddEdge(node2.Id, node5.Id);
        AddEdge(node3.Id, node5.Id);
        AddEdge(node3.Id, node6.Id);
        AddEdge(node4.Id, node7.Id);
        AddEdge(node5.Id, node7.Id);
        AddEdge(node6.Id, node7.Id);

        // Calculate initial in-degrees
        CalculateInDegrees();
    }

    private void AddEdge(int from, int to)
    {
        // Check if edge already exists
        if (edges.Exists(e => e.From == from && e.To == to))
            return;

        // Check if it would create a cycle (simple check)
        if (WouldCreateCycle(from, to))
        {
            Console.WriteLine($"Cannot add edge {from}->{to}: would create a cycle");
            return;
        }

        edges.Add(new Edge { From = from, To = to });

        // Update node's outgoing edges list
        var fromNode = nodes.Find(n => n.Id == from);
        if (fromNode != null && !fromNode.OutgoingEdges.Contains(to))
        {
            fromNode.OutgoingEdges.Add(to);
        }

        // Recalculate in-degrees
        CalculateInDegrees();
    }

    private bool WouldCreateCycle(int from, int to)
    {
        // Simple cycle detection: if to is ancestor of from, then cycle
        return IsAncestor(to, from);
    }

    private bool IsAncestor(int ancestor, int descendant)
    {
        var visited = new HashSet<int>();
        var stack = new Stack<int>();
        stack.Push(descendant);

        while (stack.Count > 0)
        {
            var current = stack.Pop();
            if (current == ancestor) return true;

            if (!visited.Contains(current))
            {
                visited.Add(current);
                var node = nodes.Find(n => n.Id == current);
                if (node != null)
                {
                    foreach (var edge in edges)
                    {
                        if (edge.From == current)
                        {
                            stack.Push(edge.To);
                        }
                    }
                }
            }
        }

        return false;
    }

    private void CalculateInDegrees()
    {
        // Reset all nodes' in-degree
        foreach (var node in nodes)
        {
            node.InDegree = 0;
        }

        // Calculate in-degrees
        foreach (var edge in edges)
        {
            var toNode = nodes.Find(n => n.Id == edge.To);
            if (toNode != null)
            {
                toNode.InDegree++;
            }
        }
    }

    private void GenerateLCSProblem()
    {
        // Enter LCS mode
        lcsMode = true;
        lcsGenerated = true;
        lcsSolving = false;
        algorithmRunning = false;
        algorithmFinished = false;
        sortedNodes.Clear();
        zeroInDegreeNodes.Clear();
        currentStep = 0;
        dpStep = 0;

        // Clear existing graph
        nodes.Clear();
        edges.Clear();
        nextNodeId = 1;

        // Reset LCS problem
        lcsProblem = new LCSProblem();

        // Generate LCS problem with guaranteed non-trivial LCS
        GenerateInterestingLCSProblem();

        // Build the DAG for LCS states
        BuildLCSGraph();

        // Initialize topological sort for LCS graph
        PrepareLCSAlgorithm();
    }

    private void GenerateInterestingLCSProblem()
    {
        Random rand = new Random();

        // Define example LCS problems that have interesting solutions
        // Each entry has: SequenceA, SequenceB, expected LCS
        (string, string, string)[] examples = {
            ("ABCD", "ACBD", "ABD"),        // Multiple common subsequences
            ("ABCBDAB", "BDCABA", "BCBA"),  // Classic example
            ("AGGTAB", "GXTXAYB", "GTAB"),  // Another classic
            ("XMJYAUZ", "MZJAWXU", "MJAU"), // Complex case
            ("ABCDEF", "ACDFGH", "ACDF"),   // Partial overlap
            ("ABCD", "ABCD", "ABCD"),       // Identical strings
            ("ABCD", "DCBA", "A"),          // Reverse order
            ("ABCDEF", "DEFGHI", "DEF"),    // Overlap at end
            ("ABCDEF", "XYZABCD", "ABCD"),  // Overlap at beginning
            ("ABCABC", "XYZABCXYZ", "ABC")  // Multiple occurrences
        };

        // Randomly select an example
        int exampleIndex = rand.Next(examples.Length);
        var example = examples[exampleIndex];

        lcsProblem.SequenceA = example.Item1;
        lcsProblem.SequenceB = example.Item2;

        // Initialize DP table
        int m = lcsProblem.SequenceA.Length;
        int n = lcsProblem.SequenceB.Length;
        lcsProblem.DP = new int[m + 1, n + 1];

        // Generate states for DP table
        lcsProblem.States.Clear();
        lcsProblem.Transitions.Clear();

        for (int i = 0; i <= m; i++)
        {
            for (int j = 0; j <= n; j++)
            {
                // Create state name
                string stateName = $"({i},{j})";
                string stateLabel = $"dp[{i},{j}]";
                lcsProblem.States.Add(stateName);

                // Add transitions based on LCS recurrence relation
                if (i > 0 && j > 0)
                {
                    if (lcsProblem.SequenceA[i - 1] == lcsProblem.SequenceB[j - 1])
                    {
                        // Match case: dp[i][j] = dp[i-1][j-1] + 1
                        lcsProblem.Transitions.Add($"({i - 1},{j - 1}) -> ({i},{j})");
                    }
                    else
                    {
                        // Mismatch case: dp[i][j] = max(dp[i-1][j], dp[i][j-1])
                        lcsProblem.Transitions.Add($"({i - 1},{j}) -> ({i},{j})");
                        lcsProblem.Transitions.Add($"({i},{j - 1}) -> ({i},{j})");
                    }
                }
                else if (i > 0)
                {
                    // Base case: first row
                    lcsProblem.Transitions.Add($"({i - 1},{j}) -> ({i},{j})");
                }
                else if (j > 0)
                {
                    // Base case: first column
                    lcsProblem.Transitions.Add($"({i},{j - 1}) -> ({i},{j})");
                }
            }
        }
    }

    private string GenerateRandomSequence(int length, Random rand)
    {
        char[] chars = { 'A', 'B', 'C', 'D', 'E', 'F', 'G' };
        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < length; i++)
        {
            sb.Append(chars[rand.Next(chars.Length)]);
        }

        return sb.ToString();
    }

    private void BuildLCSGraph()
    {
        // Clear existing nodes and edges
        nodes.Clear();
        edges.Clear();
        nextNodeId = 1;

        int m = lcsProblem.SequenceA.Length;
        int n = lcsProblem.SequenceB.Length;

        // Create nodes for each DP state
        Dictionary<string, Node> stateNodes = new Dictionary<string, Node>();

        for (int i = 0; i <= m; i++)
        {
            for (int j = 0; j <= n; j++)
            {
                // Create node for state (i,j)
                string stateName = $"({i},{j})";

                // Calculate position in a grid layout
                float x = 200 + j * 100;
                float y = 150 + i * 80;

                var node = new Node
                {
                    Id = nextNodeId++,
                    Position = new Vector2(x, y),
                    Name = stateName,
                    Label = $"dp[{i},{j}]",
                    I = i,
                    J = j
                };

                nodes.Add(node);
                stateNodes[stateName] = node;
            }
        }

        // Create edges based on LCS transitions
        foreach (var transition in lcsProblem.Transitions)
        {
            var parts = transition.Split(" -> ");
            if (parts.Length == 2 && stateNodes.ContainsKey(parts[0]) && stateNodes.ContainsKey(parts[1]))
            {
                var fromNode = stateNodes[parts[0]];
                var toNode = stateNodes[parts[1]];

                // Add edge in reverse direction for dependency graph
                // In DP, state (i,j) depends on previous states
                AddEdge(fromNode.Id, toNode.Id);
            }
        }

        // Calculate initial in-degrees
        CalculateInDegrees();
    }

    private void PrepareLCSAlgorithm()
    {
        algorithmRunning = false;
        algorithmFinished = false;
        sortedNodes.Clear();
        zeroInDegreeNodes.Clear();
        processingQueue.Clear();
        inDegreeCopy.Clear();
        currentStep = 0;

        // Reset node states
        foreach (var node in nodes)
        {
            node.IsProcessing = false;
            node.IsProcessed = false;
        }

        // Reset edge highlighting
        foreach (var edge in edges)
        {
            edge.IsHighlighted = false;
        }

        // Copy in-degrees
        foreach (var node in nodes)
        {
            inDegreeCopy[node.Id] = node.InDegree;
            if (node.InDegree == 0)
            {
                zeroInDegreeNodes.Add(node.Id);
                processingQueue.Enqueue(node.Id);
            }
        }

        // Store the initial zero in-degree nodes for display
        lcsProblem.TopologicalOrder.Clear();
        lcsProblem.DPOrder.Clear();
    }

    private void SolveLCS()
    {
        if (!lcsGenerated) return;

        lcsSolving = true;
        dpStep = 0;
        currentDPState = -1;

        int m = lcsProblem.SequenceA.Length;
        int n = lcsProblem.SequenceB.Length;

        // Clear DP table
        lcsProblem.DP = new int[m + 1, n + 1];

        // Reset DP values in nodes
        foreach (var node in nodes)
        {
            node.Value = "";
        }

        // Generate topological order for DP
        GenerateTopologicalOrderForDP();

        // Execute DP in topological order
        ExecuteDP();
    }

    private void GenerateTopologicalOrderForDP()
    {
        // Use Kahn's algorithm to get topological order
        var tempNodes = new List<Node>(nodes);
        var tempEdges = new List<Edge>(edges);

        // Calculate in-degrees
        var inDegree = new Dictionary<int, int>();
        foreach (var node in tempNodes)
        {
            inDegree[node.Id] = 0;
        }

        foreach (var edge in tempEdges)
        {
            inDegree[edge.To]++;
        }

        // Find nodes with zero in-degree
        var queue = new Queue<int>();
        foreach (var node in tempNodes)
        {
            if (inDegree[node.Id] == 0)
            {
                queue.Enqueue(node.Id);
            }
        }

        // Perform topological sort
        var topologicalOrder = new List<int>();
        while (queue.Count > 0)
        {
            var currentId = queue.Dequeue();
            topologicalOrder.Add(currentId);

            var node = tempNodes.Find(n => n.Id == currentId);
            if (node != null)
            {
                foreach (var edge in tempEdges)
                {
                    if (edge.From == currentId)
                    {
                        inDegree[edge.To]--;
                        if (inDegree[edge.To] == 0)
                        {
                            queue.Enqueue(edge.To);
                        }
                    }
                }
            }
        }

        lcsProblem.TopologicalOrder = topologicalOrder;
        lcsProblem.DPOrder = new List<int>(topologicalOrder);
    }

    private void ExecuteDP()
    {
        if (dpStep >= lcsProblem.DPOrder.Count)
        {
            // DP completed, extract LCS
            ExtractLCS();
            return;
        }

        int nodeId = lcsProblem.DPOrder[dpStep];
        var node = nodes.Find(n => n.Id == nodeId);

        if (node != null)
        {
            currentDPState = node.Id;

            int i = node.I;
            int j = node.J;

            if (i == 0 || j == 0)
            {
                // Base case
                lcsProblem.DP[i, j] = 0;
                node.Value = "0";
            }
            else if (lcsProblem.SequenceA[i - 1] == lcsProblem.SequenceB[j - 1])
            {
                // Characters match
                var prevNode = nodes.Find(n => n.I == i - 1 && n.J == j - 1);
                lcsProblem.DP[i, j] = lcsProblem.DP[i - 1, j - 1] + 1;
                node.Value = $"{lcsProblem.DP[i, j]}";

                if (prevNode != null)
                {
                    // Highlight the edge used
                    var edge = edges.Find(e => e.From == prevNode.Id && e.To == node.Id);
                    if (edge != null) edge.IsHighlighted = true;
                }
            }
            else
            {
                // Characters don't match
                int up = lcsProblem.DP[i - 1, j];
                int left = lcsProblem.DP[i, j - 1];
                lcsProblem.DP[i, j] = Math.Max(up, left);
                node.Value = $"{lcsProblem.DP[i, j]}";

                // Highlight the edge from the chosen predecessor
                if (up >= left)
                {
                    var upNode = nodes.Find(n => n.I == i - 1 && n.J == j);
                    var edge = edges.Find(e => e.From == upNode.Id && e.To == node.Id);
                    if (edge != null) edge.IsHighlighted = true;
                }
                else
                {
                    var leftNode = nodes.Find(n => n.I == i && n.J == j - 1);
                    var edge = edges.Find(e => e.From == leftNode.Id && e.To == node.Id);
                    if (edge != null) edge.IsHighlighted = true;
                }
            }

            dpStep++;
        }
    }

    private void ExtractLCS()
    {
        int m = lcsProblem.SequenceA.Length;
        int n = lcsProblem.SequenceB.Length;

        StringBuilder lcs = new StringBuilder();
        int i = m, j = n;

        while (i > 0 && j > 0)
        {
            if (lcsProblem.SequenceA[i - 1] == lcsProblem.SequenceB[j - 1])
            {
                lcs.Insert(0, lcsProblem.SequenceA[i - 1]);
                i--;
                j--;
            }
            else if (lcsProblem.DP[i - 1, j] >= lcsProblem.DP[i, j - 1])
            {
                i--;
            }
            else
            {
                j--;
            }
        }

        lcsProblem.LCS = lcs.ToString();
    }

    public void Update()
    {
        var mousePos = Raylib.GetMousePosition();

        // Handle keyboard shortcuts
        if (Raylib.IsKeyPressed(KeyboardKey.N) && !lcsMode)
            currentMode = Mode.AddNode;
        if (Raylib.IsKeyPressed(KeyboardKey.C) && !lcsMode)
            currentMode = Mode.ConnectNodes;
        if (Raylib.IsKeyPressed(KeyboardKey.Delete) && !lcsMode)
            currentMode = Mode.DeleteNode;
        if (Raylib.IsKeyPressed(KeyboardKey.E) && !lcsMode)
            currentMode = Mode.DeleteEdge;
        if (Raylib.IsKeyPressed(KeyboardKey.R))
        {
            if (lcsMode)
            {
                lcsMode = false;
                lcsGenerated = false;
                lcsSolving = false;
                Initialize(); // Reset to example graph
            }
            else
            {
                Initialize();
            }
        }
        if (Raylib.IsKeyPressed(KeyboardKey.Space))
            StartAlgorithm();
        if (Raylib.IsKeyPressed(KeyboardKey.Right))
            StepAlgorithm();
        if (Raylib.IsKeyPressed(KeyboardKey.H))
            showHelp = !showHelp;
        if (Raylib.IsKeyPressed(KeyboardKey.L))
        {
            if (!lcsMode)
            {
                GenerateLCSProblem();
            }
        }
        if (Raylib.IsKeyPressed(KeyboardKey.S))
        {
            if (lcsGenerated && !lcsSolving)
            {
                SolveLCS();
            }
        }
        if (Raylib.IsKeyPressed(KeyboardKey.D))
        {
            if (lcsSolving)
            {
                ExecuteDP();
            }
        }

        if (algorithmRunning || lcsSolving)
            return; // Pause interaction while algorithm is running

        if (lcsMode) return; // Don't allow interaction in LCS mode

        // Handle mouse interaction
        if (Raylib.IsMouseButtonPressed(MouseButton.Left))
        {
            bool clickedOnNode = false;

            // Check if clicked on a node
            for (int i = nodes.Count - 1; i >= 0; i--)
            {
                if (nodes[i].Contains(mousePos))
                {
                    clickedOnNode = true;

                    switch (currentMode)
                    {
                        case Mode.AddNode:
                            // Select node
                            selectedNode = nodes[i].Id;
                            foreach (var node in nodes)
                            {
                                node.IsSelected = node.Id == nodes[i].Id;
                            }
                            break;

                        case Mode.ConnectNodes:
                            if (!isConnecting)
                            {
                                // Start connection
                                isConnecting = true;
                                connectionStart = nodes[i].Position;
                                selectedNode = nodes[i].Id;
                            }
                            else if (selectedNode != nodes[i].Id)
                            {
                                // Complete connection
                                AddEdge(selectedNode.Value, nodes[i].Id);
                                isConnecting = false;
                                connectionStart = null;
                                selectedNode = null;
                            }
                            break;

                        case Mode.DeleteNode:
                            DeleteNode(nodes[i].Id);
                            break;

                        case Mode.DeleteEdge:
                            // Find and delete edge
                            var edgeToDelete = FindEdgeAtPosition(mousePos);
                            if (edgeToDelete != null)
                            {
                                edges.Remove(edgeToDelete);
                                CalculateInDegrees();
                            }
                            break;
                    }
                    break;
                }
            }

            // If not clicked on node and in AddNode mode, add new node
            if (!clickedOnNode && currentMode == Mode.AddNode)
            {
                var newNode = new Node
                {
                    Id = nextNodeId++,
                    Position = mousePos,
                    Name = ((char)('A' + (nextNodeId - 2) % 26)).ToString()
                };
                nodes.Add(newNode);
            }
        }

        // Handle node dragging
        if (Raylib.IsMouseButtonDown(MouseButton.Left) && selectedNode.HasValue && !lcsMode)
        {
            var node = nodes.Find(n => n.Id == selectedNode.Value);
            if (node != null)
            {
                node.Position = mousePos;
            }
        }

        // Right-click to cancel selection or connection
        if (Raylib.IsMouseButtonPressed(MouseButton.Right))
        {
            selectedNode = null;
            isConnecting = false;
            connectionStart = null;
            foreach (var node in nodes)
            {
                node.IsSelected = false;
            }
        }
    }

    private Edge FindEdgeAtPosition(Vector2 pos)
    {
        foreach (var edge in edges)
        {
            var fromNode = nodes.Find(n => n.Id == edge.From);
            var toNode = nodes.Find(n => n.Id == edge.To);

            if (fromNode != null && toNode != null)
            {
                // Calculate distance from point to line segment
                if (PointToLineDistance(pos, fromNode.Position, toNode.Position) < 10f)
                {
                    return edge;
                }
            }
        }
        return null;
    }

    private float PointToLineDistance(Vector2 point, Vector2 lineStart, Vector2 lineEnd)
    {
        var lineVec = lineEnd - lineStart;
        var pointVec = point - lineStart;

        var lineLength = lineVec.Length();
        var lineUnitVec = lineVec / lineLength;

        var projectionLength = Vector2.Dot(pointVec, lineUnitVec);

        if (projectionLength < 0)
            return pointVec.Length();
        if (projectionLength > lineLength)
            return Vector2.Distance(point, lineEnd);

        var projection = lineStart + lineUnitVec * projectionLength;
        return Vector2.Distance(point, projection);
    }

    private void DeleteNode(int nodeId)
    {
        // Delete all edges connected to this node
        edges.RemoveAll(e => e.From == nodeId || e.To == nodeId);

        // Remove from other nodes' outgoing edges lists
        foreach (var node in nodes)
        {
            node.OutgoingEdges.RemoveAll(id => id == nodeId);
        }

        // Delete the node
        nodes.RemoveAll(n => n.Id == nodeId);

        // Recalculate in-degrees
        CalculateInDegrees();
    }

    public void StartAlgorithm()
    {
        if (algorithmRunning || algorithmFinished)
            return;

        algorithmRunning = true;
        algorithmFinished = false;
        sortedNodes.Clear();
        zeroInDegreeNodes.Clear();
        processingQueue.Clear();
        inDegreeCopy.Clear();
        currentStep = 0;

        // Reset node states
        foreach (var node in nodes)
        {
            node.IsProcessing = false;
            node.IsProcessed = false;
        }

        // Reset edge highlighting
        foreach (var edge in edges)
        {
            edge.IsHighlighted = false;
        }

        // Copy in-degrees
        foreach (var node in nodes)
        {
            inDegreeCopy[node.Id] = node.InDegree;
            if (node.InDegree == 0)
            {
                zeroInDegreeNodes.Add(node.Id);
                processingQueue.Enqueue(node.Id);
            }
        }

        // Execute first step
        StepAlgorithm();
    }

    public void StepAlgorithm()
    {
        if (!algorithmRunning || algorithmFinished)
            return;

        currentStep++;

        // Process all nodes with in-degree 0 in current queue
        var nodesToProcess = new List<int>();
        while (processingQueue.Count > 0)
        {
            nodesToProcess.Add(processingQueue.Dequeue());
        }

        // Mark these nodes as processing
        foreach (var nodeId in nodesToProcess)
        {
            var node = nodes.Find(n => n.Id == nodeId);
            if (node != null)
            {
                node.IsProcessing = true;
            }
        }

        // Add nodes to sorted result
        foreach (var nodeId in nodesToProcess)
        {
            sortedNodes.Add(nodeId);
            var node = nodes.Find(n => n.Id == nodeId);
            if (node != null)
            {
                node.IsProcessing = false;
                node.IsProcessed = true;

                // Decrease in-degree of successor nodes
                foreach (var edge in edges)
                {
                    if (edge.From == nodeId)
                    {
                        edge.IsHighlighted = true;
                        inDegreeCopy[edge.To]--;
                        if (inDegreeCopy[edge.To] == 0)
                        {
                            zeroInDegreeNodes.Add(edge.To);
                            processingQueue.Enqueue(edge.To);
                        }
                    }
                }
            }
        }

        // Update zero in-degree nodes list for display
        zeroInDegreeNodes.Clear();
        foreach (var kvp in inDegreeCopy)
        {
            if (kvp.Value == 0 && !sortedNodes.Contains(kvp.Key))
            {
                zeroInDegreeNodes.Add(kvp.Key);
            }
        }

        // Check if algorithm is finished
        if (processingQueue.Count == 0 && zeroInDegreeNodes.Count == 0)
        {
            algorithmRunning = false;
            algorithmFinished = true;

            // Check for cycles
            if (sortedNodes.Count != nodes.Count)
            {
                Console.WriteLine("Warning: Graph contains a cycle!");
            }
        }
    }

    public void Draw()
    {
        // Draw background
        Raylib.ClearBackground(new Color(240, 240, 245, 255));

        // Draw connection line (under nodes)
        if (isConnecting && connectionStart.HasValue && !lcsMode)
        {
            var mousePos = Raylib.GetMousePosition();
            Raylib.DrawLineEx(connectionStart.Value, mousePos, 3, edgeColor);
        }

        // Draw edges
        foreach (var edge in edges)
        {
            var fromNode = nodes.Find(n => n.Id == edge.From);
            var toNode = nodes.Find(n => n.Id == edge.To);

            if (fromNode != null && toNode != null)
            {
                var color = edge.IsHighlighted ? highlightedEdgeColor : edgeColor;
                var thickness = edge.IsHighlighted ? 3f : 2f;

                // Draw arrow
                DrawArrow(fromNode.Position, toNode.Position, color, thickness);
            }
        }

        // Draw nodes
        foreach (var node in nodes)
        {
            Color color = lcsMode ? lcsNodeColor : nodeColor;
            if (node.IsSelected && !lcsMode) color = selectedColor;
            if (node.IsProcessing) color = processingColor;
            if (node.IsProcessed) color = processedColor;
            if (lcsSolving && currentDPState == node.Id) color = lcsHighlightColor;

            // Draw node
            Raylib.DrawCircleV(node.Position, node.Radius, color);
            Raylib.DrawCircleLines((int)node.Position.X, (int)node.Position.Y, node.Radius, Color.Black);

            // Draw node name
            var textSize = Raylib.MeasureText(node.Name, lcsMode ? 16 : 20);
            Raylib.DrawText(node.Name,
                (int)(node.Position.X - textSize / 2),
                (int)(node.Position.Y - (lcsMode ? 20 : 10)),
                lcsMode ? 16 : 20, Color.Black);

            // Draw additional info for LCS nodes
            if (lcsMode && !string.IsNullOrEmpty(node.Label))
            {
                var labelSize = Raylib.MeasureText(node.Label, 12);
                Raylib.DrawText(node.Label,
                    (int)(node.Position.X - labelSize / 2),
                    (int)(node.Position.Y),
                    12, Color.DarkBlue);

                if (!string.IsNullOrEmpty(node.Value))
                {
                    var valueSize = Raylib.MeasureText(node.Value, 14);
                    Raylib.DrawText(node.Value,
                        (int)(node.Position.X - valueSize / 2),
                        (int)(node.Position.Y + 15),
                        14, Color.Red); // Changed from DarkRed to Red
                }
            }
            else if (!lcsMode)
            {
                // Draw in-degree
                Raylib.DrawText($"In: {node.InDegree}",
                    (int)(node.Position.X - 20),
                    (int)(node.Position.Y + 25),
                    12, Color.DarkGray);
            }
        }

        // Draw info panel (right)
        DrawInfoPanel();

        // Draw LCS panel (middle)
        DrawLCSPanel();

        // Draw control panel
        DrawControlPanel();

        // Draw help info
        if (showHelp)
        {
            DrawHelpPanel();
        }
    }

    private void DrawArrow(Vector2 start, Vector2 end, Color color, float thickness)
    {
        // Draw line
        Raylib.DrawLineEx(start, end, thickness, color);

        // Calculate arrow direction
        var direction = Vector2.Normalize(end - start);
        var arrowLength = 15f;
        var arrowAngle = 30f * MathF.PI / 180f;

        // Calculate arrow side points
        var left = new Vector2(
            end.X - arrowLength * MathF.Cos(MathF.Atan2(direction.Y, direction.X) + arrowAngle),
            end.Y - arrowLength * MathF.Sin(MathF.Atan2(direction.Y, direction.X) + arrowAngle)
        );

        var right = new Vector2(
            end.X - arrowLength * MathF.Cos(MathF.Atan2(direction.Y, direction.X) - arrowAngle),
            end.Y - arrowLength * MathF.Sin(MathF.Atan2(direction.Y, direction.X) - arrowAngle)
        );

        // Draw arrow
        Raylib.DrawLineEx(end, left, thickness, color);
        Raylib.DrawLineEx(end, right, thickness, color);
    }

    private void DrawInfoPanel()
    {
        int panelWidth = 300;
        int panelHeight = Raylib.GetScreenHeight();
        int panelX = Raylib.GetScreenWidth() - panelWidth;

        // Draw panel background
        Raylib.DrawRectangle(panelX, 0, panelWidth, panelHeight, new Color(245, 245, 250, 255));
        Raylib.DrawRectangleLines(panelX, 0, panelWidth, panelHeight, new Color(200, 200, 210, 255));

        // Draw title
        if (lcsMode)
        {
            Raylib.DrawText("LCS Topological Order", panelX + 10, 20, 20, Color.DarkBlue);
        }
        else
        {
            Raylib.DrawText("Topological Sort (Kahn's Algorithm)", panelX + 10, 20, 20, Color.DarkBlue);
        }

        // Draw current mode
        string modeText = $"Mode: {GetModeName()}";
        if (lcsMode) modeText = "Mode: LCS Problem";
        Raylib.DrawText(modeText, panelX + 10, 60, 18, Color.DarkBlue);

        // Draw algorithm status
        Raylib.DrawText($"Algorithm Status:", panelX + 10, 100, 18, Color.DarkBlue);
        string statusText = algorithmFinished ? "Finished" : algorithmRunning ? "Running" : "Not Started";
        if (lcsSolving) statusText = "Solving LCS (DP)";
        Raylib.DrawText($"  {statusText}", panelX + 20, 130, 16,
            algorithmFinished ? Color.Green : algorithmRunning ? Color.Orange :
            lcsSolving ? Color.Purple : Color.Gray);

        Raylib.DrawText($"Step: {currentStep}", panelX + 20, 160, 16, Color.DarkGray);
        if (lcsSolving)
        {
            Raylib.DrawText($"DP Step: {dpStep}/{lcsProblem.DPOrder.Count}", panelX + 20, 185, 16, Color.DarkPurple);
        }

        // Draw topological sort result
        Raylib.DrawText($"Topological Order:", panelX + 10, 220, 18, Color.DarkBlue);
        string sortedText = "";

        if (lcsMode && lcsProblem.TopologicalOrder.Count > 0)
        {
            foreach (var nodeId in lcsProblem.TopologicalOrder)
            {
                var node = nodes.Find(n => n.Id == nodeId);
                sortedText += node?.Name + " -> ";
            }
        }
        else
        {
            foreach (var nodeId in sortedNodes)
            {
                var node = nodes.Find(n => n.Id == nodeId);
                sortedText += node?.Name + " -> ";
            }
        }

        if (sortedText.Length > 0)
            sortedText = sortedText.Substring(0, sortedText.Length - 3);
        else
            sortedText = "Not started";

        Raylib.DrawText(sortedText, panelX + 20, 250, 14, Color.DarkGreen);

        // Draw current in-degree 0 nodes
        Raylib.DrawText($"Zero In-Degree Nodes:", panelX + 10, 300, 18, Color.DarkBlue);
        string zeroDegreeText = "";
        foreach (var nodeId in zeroInDegreeNodes)
        {
            var node = nodes.Find(n => n.Id == nodeId);
            if (node != null && !node.IsProcessed)
            {
                zeroDegreeText += node.Name + " ";
            }
        }
        if (string.IsNullOrEmpty(zeroDegreeText))
            zeroDegreeText = "None";

        Raylib.DrawText(zeroDegreeText, panelX + 20, 330, 16, Color.Red);

        // Draw node in-degree table
        if (!lcsMode)
        {
            Raylib.DrawText($"In-Degree Table:", panelX + 10, 380, 18, Color.DarkBlue);
            int yPos = 410;
            foreach (var node in nodes)
            {
                var currentInDegree = inDegreeCopy.ContainsKey(node.Id) ? inDegreeCopy[node.Id] : node.InDegree;
                Raylib.DrawText($"  {node.Name}: {currentInDegree}", panelX + 20, yPos, 16, Color.DarkGray);
                yPos += 25;
            }
        }
    }

    private void DrawLCSPanel()
    {
        int panelWidth = 350;
        int panelHeight = Raylib.GetScreenHeight();
        int panelX = Raylib.GetScreenWidth() - 300 - panelWidth; // Between graph and info panel

        // Draw panel background
        Raylib.DrawRectangle(panelX, 0, panelWidth, panelHeight, new Color(250, 250, 255, 255));
        Raylib.DrawRectangleLines(panelX, 0, panelWidth, panelHeight, new Color(210, 210, 220, 255));

        // Draw title
        Raylib.DrawText("LCS Problem", panelX + 10, 20, 24, Color.DarkBlue);

        if (!lcsGenerated)
        {
            Raylib.DrawText("Press 'L' to generate", panelX + 50, 100, 20, Color.Gray);
            Raylib.DrawText("an LCS problem", panelX + 70, 130, 20, Color.Gray);
            return;
        }

        // Draw LCS sequences
        Raylib.DrawText($"Sequence A: {lcsProblem.SequenceA}", panelX + 10, 70, 20, Color.Green);
        Raylib.DrawText($"Sequence B: {lcsProblem.SequenceB}", panelX + 10, 100, 20, Color.Green);

        // Draw DP table
        if (lcsProblem.DP != null)
        {
            Raylib.DrawText("DP Table:", panelX + 10, 140, 18, Color.DarkBlue);

            int m = lcsProblem.SequenceA.Length;
            int n = lcsProblem.SequenceB.Length;
            int cellSize = 40;
            int startX = panelX + 20;
            int startY = 180;

            // Draw column headers (Sequence B)
            Raylib.DrawText(" ", startX, startY, 16, Color.Black);
            for (int j = 0; j <= n; j++)
            {
                string header = j == 0 ? " " : lcsProblem.SequenceB[j - 1].ToString();
                Raylib.DrawText(header, startX + (j + 1) * cellSize + 10, startY, 16, Color.Red); // Changed from DarkRed to Red
            }

            // Draw row headers and table
            for (int i = 0; i <= m; i++)
            {
                // Row header (Sequence A)
                string rowHeader = i == 0 ? " " : lcsProblem.SequenceA[i - 1].ToString();
                Raylib.DrawText(rowHeader, startX, startY + (i + 1) * cellSize + 10, 16, Color.Red); // Changed from DarkRed to Red

                for (int j = 0; j <= n; j++)
                {
                    // Draw cell
                    float cellX = startX + (j + 1) * cellSize;
                    float cellY = startY + (i + 1) * cellSize;

                    Color cellColor = (i == 0 || j == 0) ? Color.LightGray : Color.White;
                    if (lcsSolving && i == dpStep / (n + 1) && j == dpStep % (n + 1))
                        cellColor = new Color(255, 200, 150, 255);

                    Raylib.DrawRectangle((int)cellX, (int)cellY, cellSize, cellSize, cellColor);
                    Raylib.DrawRectangleLines((int)cellX, (int)cellY, cellSize, cellSize, Color.Gray);

                    // Draw DP value
                    string value = lcsProblem.DP[i, j].ToString();
                    if (i == 0 && j == 0) value = "0";
                    Raylib.DrawText(value,
                        (int)(cellX + cellSize / 2 - 5),
                        (int)(cellY + cellSize / 2 - 8),
                        16, Color.Black);
                }
            }

            // Draw LCS result
            int tableBottom = startY + (m + 2) * cellSize + 20;
            Raylib.DrawText($"LCS Result: {lcsProblem.LCS}", panelX + 10, tableBottom, 20, Color.Purple);
            Raylib.DrawText($"Length: {lcsProblem.LCS.Length}", panelX + 10, tableBottom + 30, 18, Color.DarkBlue);

            // Draw state transitions
            int transitionsY = tableBottom + 70;
            Raylib.DrawText("State Transitions:", panelX + 10, transitionsY, 18, Color.DarkBlue);

            transitionsY += 30;
            int maxTransitions = 10;
            for (int i = 0; i < Math.Min(maxTransitions, lcsProblem.Transitions.Count); i++)
            {
                Raylib.DrawText($"  {lcsProblem.Transitions[i]}", panelX + 20, transitionsY, 14, Color.DarkGray);
                transitionsY += 20;
            }

            if (lcsProblem.Transitions.Count > maxTransitions)
            {
                Raylib.DrawText($"  ... and {lcsProblem.Transitions.Count - maxTransitions} more",
                    panelX + 20, transitionsY, 12, Color.Gray);
            }
        }
    }

    private void DrawControlPanel()
    {
        int panelWidth = Raylib.GetScreenWidth() - 300 - 350; // Account for LCS panel
        int panelHeight = 60;
        int panelY = Raylib.GetScreenHeight() - panelHeight;

        // Draw control panel background
        Raylib.DrawRectangle(0, panelY, panelWidth, panelHeight, new Color(230, 230, 240, 255));
        Raylib.DrawRectangleLines(0, panelY, panelWidth, panelHeight, new Color(200, 200, 210, 255));

        // Draw control buttons
        int buttonWidth = 130;
        int buttonHeight = 40;
        int buttonSpacing = 10;
        int buttonY = panelY + 10;
        int buttonX = 10;

        if (!lcsMode)
        {
            // Mode buttons (only in normal mode)
            DrawButton(buttonX, buttonY, buttonWidth, buttonHeight, $"Add Node (N)",
                currentMode == Mode.AddNode ? Color.SkyBlue : Color.LightGray);
            buttonX += buttonWidth + buttonSpacing;

            DrawButton(buttonX, buttonY, buttonWidth, buttonHeight, $"Connect (C)",
                currentMode == Mode.ConnectNodes ? Color.SkyBlue : Color.LightGray);
            buttonX += buttonWidth + buttonSpacing;

            DrawButton(buttonX, buttonY, buttonWidth, buttonHeight, $"Del Node (Del)",
                currentMode == Mode.DeleteNode ? Color.SkyBlue : Color.LightGray);
            buttonX += buttonWidth + buttonSpacing;

            DrawButton(buttonX, buttonY, buttonWidth, buttonHeight, $"Del Edge (E)",
                currentMode == Mode.DeleteEdge ? Color.SkyBlue : Color.LightGray);
            buttonX += buttonWidth + buttonSpacing;
        }

        // Algorithm control buttons
        if (!lcsMode)
        {
            DrawButton(buttonX, buttonY, buttonWidth, buttonHeight, $"Start/Reset (Space)",
                algorithmRunning ? Color.Orange : Color.Green);
            buttonX += buttonWidth + buttonSpacing;

            DrawButton(buttonX, buttonY, buttonWidth, buttonHeight, $"Step (->)",
                Color.SkyBlue);
            buttonX += buttonWidth + buttonSpacing;
        }

        // LCS buttons
        DrawButton(buttonX, buttonY, buttonWidth, buttonHeight,
            lcsMode ? "Exit LCS (R)" : "Generate LCS (L)",
            lcsMode ? Color.Pink : new Color(144, 238, 144, 255)); // LightGreen
        buttonX += buttonWidth + buttonSpacing;

        if (lcsGenerated && !lcsSolving)
        {
            DrawButton(buttonX, buttonY, buttonWidth, buttonHeight, $"Solve LCS (S)",
                new Color(147, 112, 219, 255)); // MediumPurple
            buttonX += buttonWidth + buttonSpacing;
        }

        if (lcsSolving)
        {
            DrawButton(buttonX, buttonY, buttonWidth, buttonHeight, $"DP Step (D)",
                Color.Orange);
            buttonX += buttonWidth + buttonSpacing;
        }

        // Help button
        DrawButton(Raylib.GetScreenWidth() - 300 - 350 - 120, buttonY, 110, buttonHeight,
            showHelp ? "Hide Help (H)" : "Show Help (H)", Color.Gold);
    }

    private void DrawButton(int x, int y, int width, int height, string text, Color color)
    {
        Raylib.DrawRectangle(x, y, width, height, color);
        Raylib.DrawRectangleLines(x, y, width, height, Color.Black);

        var textSize = Raylib.MeasureText(text, 14);
        Raylib.DrawText(text, x + (width - textSize) / 2, y + (height - 14) / 2, 14, Color.Black);
    }

    private void DrawHelpPanel()
    {
        int panelWidth = 500;
        int panelHeight = 350;
        int panelX = (Raylib.GetScreenWidth() - panelWidth) / 2;
        int panelY = (Raylib.GetScreenHeight() - panelHeight) / 2;

        // Draw semi-transparent background
        Raylib.DrawRectangle(panelX, panelY, panelWidth, panelHeight, new Color(0, 0, 0, 200));
        Raylib.DrawRectangleLines(panelX, panelY, panelWidth, panelHeight, Color.White);

        // Draw title
        Raylib.DrawText("Topological Sort Demo - Help", panelX + 10, panelY + 10, 24, Color.White);

        // Draw help content
        int textY = panelY + 50;

        if (lcsMode)
        {
            Raylib.DrawText("LCS Mode:", panelX + 20, textY, 20, Color.Yellow);
            textY += 30;

            string[] lcsHelpLines = {
                "• LCS (Longest Common Subsequence) Problem",
                "• States: dp[i,j] = LCS length for A[0..i-1], B[0..j-1]",
                "• Recurrence:",
                "  - if A[i-1] == B[j-1]: dp[i,j] = dp[i-1,j-1] + 1",
                "  - else: dp[i,j] = max(dp[i-1,j], dp[i,j-1])",
                "• DAG: States as nodes, dependencies as edges",
                "• Solving: Topological order -> DP computation",
                "",
                "Interesting Examples:",
                "• ABCD vs ACBD: LCS = ABD (multiple common subsequences)",
                "• ABCBDAB vs BDCABA: LCS = BCBA (classic textbook example)",
                "• AGGTAB vs GXTXAYB: LCS = GTAB",
                "• XMJYAUZ vs MZJAWXU: LCS = MJAU (complex case)",
                "",
                "Controls:",
                "• L: Generate LCS problem",
                "• S: Solve LCS using DP",
                "• D: Step through DP computation",
                "• R: Exit LCS mode",
                "• H: Show/Hide help"
            };

            foreach (var line in lcsHelpLines)
            {
                Raylib.DrawText(line, panelX + 20, textY, 16, Color.White);
                textY += 22;
            }
        }
        else
        {
            Raylib.DrawText("Kahn's Algorithm Steps:", panelX + 20, textY, 20, Color.Yellow);
            textY += 30;

            string[] helpLines = {
                "1. Find nodes with in-degree 0, add to queue",
                "2. Remove node from queue, add to sorted list",
                "3. Remove all outgoing edges from this node",
                "4. Update in-degree of connected nodes",
                "5. Repeat until queue is empty",
                "",
                "Interaction:",
                "• Add Node: Click empty area",
                "• Connect Nodes: Select connect mode, click start & end",
                "• Delete Node/Edge: Select delete mode, click target",
                "• Drag Node: Select and drag",
                "",
                "Shortcuts:",
                "• N/C/Del/E: Switch mode",
                "• Space: Start/Reset algorithm",
                "• ->: Step forward",
                "• R: Reset graph",
                "• L: Enter LCS mode",
                "• H: Show/Hide help"
            };

            foreach (var line in helpLines)
            {
                Raylib.DrawText(line, panelX + 20, textY, 16, Color.White);
                textY += 22;
            }
        }
    }

    private string GetModeName()
    {
        return currentMode switch
        {
            Mode.AddNode => "Add Node",
            Mode.ConnectNodes => "Connect Nodes",
            Mode.DeleteNode => "Delete Node",
            Mode.DeleteEdge => "Delete Edge",
            _ => "Unknown"
        };
    }
}

// Main program
public static class Program
{
    public static void Main()
    {
        const int screenWidth = 1500;
        const int screenHeight = 800;

        Raylib.InitWindow(screenWidth, screenHeight, "Topological Sort Demo - Kahn's Algorithm with LCS");
        Raylib.SetTargetFPS(60);

        var demo = new ToposortDemo();
        demo.Initialize();

        while (!Raylib.WindowShouldClose())
        {
            demo.Update();

            Raylib.BeginDrawing();
            demo.Draw();
            Raylib.EndDrawing();
        }

        Raylib.CloseWindow();
    }
}