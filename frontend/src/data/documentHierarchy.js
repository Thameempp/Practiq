/**
 * Document hierarchy and semantic content map for 'Computer Science: An Introduction'
 * Structured into Chapters, Sections, and Subsections for ASCII tree rendering.
 */

export const DOCUMENT_HIERARCHY = [
  {
    id: 'ch-1',
    title: 'Chapter 1: What Is Computer Science?',
    page: 1,
    pageLabel: 'p. 1',
    summary: 'Definitions of computation, problem-solving, abstraction, automation, and efficiency.',
    excerpt: `Computer Science is the study of computation, information, algorithms, and computer systems. It is not limited to using computers; instead, it explains how problems can be represented, solved, automated, and analyzed efficiently. Computer scientists study both theoretical ideas and practical systems.

A computer follows instructions. These instructions may be written using programming languages such as Python, Java, C++, or JavaScript. The instructions are processed by hardware and software to produce useful results.

Important characteristics:
• Problem-solving: breaking a complex problem into smaller steps.
• Abstraction: hiding unnecessary details and focusing on the essential parts.
• Automation: allowing a system to perform repeated tasks automatically.
• Efficiency: reducing execution time, memory usage, or other resources.`,
    children: [
      {
        id: 'sec-1-1',
        title: '1.1 Core Foundations',
        page: 1,
        pageLabel: 'p. 1',
        summary: 'Computation and programming language execution.',
        excerpt: `Computer Science is the study of computation, information, algorithms, and computer systems. Instructions may be written using programming languages such as Python, Java, C++, or JavaScript.`,
        children: [
          {
            id: 'sub-1-1-1',
            title: 'Problem-Solving',
            page: 1,
            pageLabel: 'p. 1',
            summary: 'Breaking complex problems into small solvable steps.',
            excerpt: `Problem-solving: breaking a complex problem into smaller steps.`,
          },
          {
            id: 'sub-1-1-2',
            title: 'Abstraction & Automation',
            page: 1,
            pageLabel: 'p. 1',
            summary: 'Hiding details and automating repetitive tasks.',
            excerpt: `Abstraction: hiding unnecessary details and focusing on essential parts.\nAutomation: allowing a system to perform repeated tasks automatically.`,
          },
          {
            id: 'sub-1-1-3',
            title: 'Efficiency',
            page: 1,
            pageLabel: 'p. 1',
            summary: 'Minimizing compute time, memory usage, and resources.',
            excerpt: `Efficiency: reducing execution time, memory usage, or other resources.`,
          },
        ],
      },
    ],
  },
  {
    id: 'ch-2',
    title: 'Chapter 2: Major Areas of Computer Science',
    page: 1,
    pageLabel: 'p. 1',
    summary: 'Taxonomy of interconnected fields in computer science.',
    excerpt: `Computer Science contains several interconnected areas:
• Algorithms and Data Structures: Methods for solving problems and organizing data.
• Programming Languages: Formal languages used to express computational instructions.
• Operating Systems: Software that manages hardware, memory, processes, and files.
• Computer Networks: Systems that allow computers and devices to communicate.
• Databases: Organized collections of data that can be stored, searched, and updated.
• Artificial Intelligence: Techniques that enable machines to perform tasks requiring intelligent behavior.
• Cybersecurity: Practices for protecting systems, networks, and information.`,
    children: [
      {
        id: 'sec-2-1',
        title: '2.1 Subfield Taxonomy',
        page: 1,
        pageLabel: 'p. 1',
        summary: 'Seven key areas of computing.',
        excerpt: `Each area focuses on a different aspect of computing, but real-world applications often combine multiple areas.`,
        children: [
          {
            id: 'sub-2-1-1',
            title: 'Algorithms & Languages',
            page: 1,
            pageLabel: 'p. 1',
            summary: 'Problem solving methods and formal instruction languages.',
            excerpt: `Algorithms and Data Structures: Methods for solving problems and organizing data.\nProgramming Languages: Formal languages used to express computational instructions.`,
          },
          {
            id: 'sub-2-1-2',
            title: 'Systems, Networks & DB',
            page: 1,
            pageLabel: 'p. 1',
            summary: 'Operating systems, network communications, and database persistence.',
            excerpt: `Operating Systems: Software that manages hardware, memory, processes, and files.\nComputer Networks: Systems that allow computers and devices to communicate.\nDatabases: Organized collections of data.`,
          },
          {
            id: 'sub-2-1-3',
            title: 'AI & Cybersecurity',
            page: 1,
            pageLabel: 'p. 1',
            summary: 'Intelligent behavior systems and security protection.',
            excerpt: `Artificial Intelligence: Techniques that enable machines to perform intelligent tasks.\nCybersecurity: Practices for protecting systems, networks, and information.`,
          },
        ],
      },
    ],
  },
  {
    id: 'ch-3',
    title: 'Chapter 3: Algorithms and Data Structures',
    page: 2,
    pageLabel: 'p. 2',
    summary: 'Algorithms recipe analogy, 7 common data structures, and linear search.',
    excerpt: `An algorithm is a finite sequence of clear instructions used to solve a problem. For example, a recipe is an everyday analogy for an algorithm: it contains ordered steps, required inputs, and an expected result.

A data structure is a method of organizing and storing data so that it can be accessed and modified efficiently.`,
    children: [
      {
        id: 'sec-3-1',
        title: '3.1 Common Data Structures',
        page: 2,
        pageLabel: 'p. 2',
        summary: 'Array, Linked List, Stack, Queue, Tree, Graph, Hash Table.',
        excerpt: `Common data structures:
• Array: Stores elements in an indexed sequence.
• Linked List: Stores elements as connected nodes.
• Stack: Follows the Last-In, First-Out principle (LIFO).
• Queue: Follows the First-In, First-Out principle (FIFO).
• Tree: Represents hierarchical relationships.
• Graph: Represents connections between objects or vertices.
• Hash Table: Stores key-value pairs for fast average lookup.`,
        children: [
          {
            id: 'sub-3-1-1',
            title: 'Linear Collections',
            page: 2,
            pageLabel: 'p. 2',
            summary: 'Array, Linked List, Stack (LIFO), Queue (FIFO).',
            excerpt: `Array: Stores elements in an indexed sequence.\nLinked List: Stores elements as connected nodes.\nStack: LIFO.\nQueue: FIFO.`,
          },
          {
            id: 'sub-3-1-2',
            title: 'Hierarchical & Graphs',
            page: 2,
            pageLabel: 'p. 2',
            summary: 'Trees, Graphs, and Hash Tables.',
            excerpt: `Tree: Represents hierarchical relationships.\nGraph: Represents connections between vertices.\nHash Table: Stores key-value pairs for fast average lookup.`,
          },
        ],
      },
      {
        id: 'sec-3-2',
        title: '3.2 Linear Search Example',
        page: 2,
        pageLabel: 'p. 2',
        summary: 'Sequential search, O(n) complexity, and Python code.',
        excerpt: `Linear search checks each element in a collection, one after another, until the target is found or the collection ends. If there are n elements, the worst-case time complexity is O(n).

Python example:
numbers = [4, 8, 15, 16, 23, 42]
target = 23
for number in numbers:
    if number == target:
        print('Found:', number)`,
        children: [
          {
            id: 'sub-3-2-1',
            title: 'Time Complexity O(n)',
            page: 2,
            pageLabel: 'p. 2',
            summary: 'Worst-case search time complexity.',
            excerpt: `If there are n elements, the worst-case time complexity is O(n).`,
          },
          {
            id: 'sub-3-2-2',
            title: 'Python Implementation',
            page: 2,
            pageLabel: 'p. 2',
            summary: 'Python code snippet iterating over list.',
            excerpt: `numbers = [4, 8, 15, 16, 23, 42]
target = 23
for number in numbers:
    if number == target:
        print('Found:', number)`,
          },
        ],
      },
    ],
  },
  {
    id: 'ch-4',
    title: 'Chapter 4: Programming & Software Dev',
    page: 2,
    pageLabel: 'p. 2',
    summary: 'Programming logic vs overall software development lifecycle.',
    excerpt: `Programming is the process of writing instructions that a computer can execute. A program usually contains variables, data types, conditions, loops, functions, and error-handling logic.

Software development is broader than programming. It may include planning, requirement analysis, design, coding, testing, deployment, documentation, and maintenance. A reliable application should be readable, secure, maintainable, and tested.`,
    children: [
      {
        id: 'sec-4-1',
        title: '4.1 Development Lifecycle',
        page: 2,
        pageLabel: 'p. 2',
        summary: 'Planning, design, coding, testing, and deployment.',
        excerpt: `Planning, requirement analysis, design, coding, testing, deployment, documentation, and maintenance.`,
        children: [
          {
            id: 'sub-4-1-1',
            title: 'Design & Coding',
            page: 2,
            pageLabel: 'p. 2',
            summary: 'Variables, data types, loops, functions, and error handling.',
            excerpt: `Variables, data types, conditions, loops, functions, and error-handling logic.`,
          },
          {
            id: 'sub-4-1-2',
            title: 'Testing & Maintainability',
            page: 2,
            pageLabel: 'p. 2',
            summary: 'Reliable, readable, and secure code practices.',
            excerpt: `A reliable application should be readable, secure, maintainable, and tested.`,
          },
        ],
      },
    ],
  },
  {
    id: 'ch-5',
    title: 'Chapter 5: Computer Hardware and Software',
    page: 3,
    pageLabel: 'p. 3',
    summary: 'Physical components and distinction between system and application software.',
    excerpt: `Computer hardware refers to the physical components of a computer (CPU, RAM, SSD/HDD, GPU, Motherboard). Software refers to instructions that operate on hardware.`,
    children: [
      {
        id: 'sec-5-1',
        title: '5.1 Hardware Components',
        page: 3,
        pageLabel: 'p. 3',
        summary: 'CPU, RAM, Storage, GPU, and Motherboard.',
        excerpt: `• CPU: Executes instructions and performs calculations.
• RAM: Temporarily stores data and instructions currently in use.
• SSD/HDD: Stores files and programs permanently.
• GPU: Processes graphics and parallel computations.
• Motherboard: Connects major hardware components.`,
        children: [
          {
            id: 'sub-5-1-1',
            title: 'Compute & Memory',
            page: 3,
            pageLabel: 'p. 3',
            summary: 'CPU execution and RAM temporary storage.',
            excerpt: `CPU: Executes instructions. RAM: Temporarily stores active data.`,
          },
          {
            id: 'sub-5-1-2',
            title: 'Storage & GPU',
            page: 3,
            pageLabel: 'p. 3',
            summary: 'Persistent SSD storage and GPU parallel processing.',
            excerpt: `SSD/HDD: Persistent files. GPU: Parallel calculations.`,
          },
        ],
      },
      {
        id: 'sec-5-2',
        title: '5.2 System vs Application Software',
        page: 3,
        pageLabel: 'p. 3',
        summary: 'OS level management vs end-user productivity programs.',
        excerpt: `System software manages the computer, while application software helps users perform specific tasks.`,
        children: [],
      },
    ],
  },
  {
    id: 'ch-6',
    title: 'Chapter 6: Databases and Information',
    page: 3,
    pageLabel: 'p. 3',
    summary: 'Relational databases, DBMS operations, and SQL filtering.',
    excerpt: `A database stores structured or semi-structured information. A Database Management System (DBMS) provides tools to create, read, update, delete, and manage data. SQL is commonly used to work with relational databases.`,
    children: [
      {
        id: 'sec-6-1',
        title: '6.1 Relational Concepts',
        page: 3,
        pageLabel: 'p. 3',
        summary: 'Tables, rows, and structured queries.',
        excerpt: `A student database may contain student IDs, names, courses, grades, and attendance records.`,
        children: [],
      },
      {
        id: 'sec-6-2',
        title: '6.2 SQL Query Example',
        page: 3,
        pageLabel: 'p. 3',
        summary: 'SELECT and WHERE filtering statement.',
        excerpt: `SELECT name, grade
FROM students
WHERE grade >= 80;`,
        children: [],
      },
    ],
  },
  {
    id: 'ch-7',
    title: 'Chapter 7: Artificial Intelligence and ML',
    page: 3,
    pageLabel: 'pp. 3-4',
    summary: 'Perception, reasoning, models learning patterns from data, and the 6-step workflow.',
    excerpt: `Artificial Intelligence (AI) focuses on perception, reasoning, language, and planning. Machine Learning (ML) models learn patterns from data instead of being explicitly programmed.`,
    children: [
      {
        id: 'sec-7-1',
        title: '7.1 AI vs Machine Learning',
        page: 3,
        pageLabel: 'p. 3',
        summary: 'Rule-based systems vs pattern learning models.',
        excerpt: `Models learn patterns from data instead of being explicitly programmed for every rule.`,
        children: [],
      },
      {
        id: 'sec-7-2',
        title: '7.2 6-Step ML Workflow',
        page: 4,
        pageLabel: 'pp. 3-4',
        summary: 'Collect, clean, feature engineer, train, evaluate, and deploy.',
        excerpt: `1. Collect and understand the data.
2. Clean the data and handle missing or incorrect values.
3. Select useful features or representations.
4. Train a model using a suitable algorithm.
5. Evaluate the model with appropriate metrics.
6. Deploy, monitor, and improve the model.`,
        children: [
          {
            id: 'sub-7-2-1',
            title: 'Data Prep & Features',
            page: 4,
            pageLabel: 'p. 3',
            summary: 'Collection, cleaning, and feature selection.',
            excerpt: `Collect data, clean missing values, select useful representations.`,
          },
          {
            id: 'sub-7-2-2',
            title: 'Training & Evaluation',
            page: 4,
            pageLabel: 'p. 3',
            summary: 'Algorithm training and metric evaluation.',
            excerpt: `Train a model using a suitable algorithm and evaluate with metrics.`,
          },
          {
            id: 'sub-7-2-3',
            title: 'Deployment & Monitoring',
            page: 4,
            pageLabel: 'p. 4',
            summary: 'Deploying to production and monitoring quality.',
            excerpt: `Deploy, monitor, and improve the model.`,
          },
        ],
      },
    ],
  },
  {
    id: 'ch-8',
    title: 'Chapter 8: Networks and the Internet',
    page: 5,
    pageLabel: 'p. 5',
    summary: 'Communication protocols, TCP/IP, DNS, HTTP/HTTPS, IP addresses, bandwidth, and latency.',
    excerpt: `A computer network connects devices to exchange data and share resources. Uses TCP/IP, DNS for domain resolution, and HTTP/HTTPS for web resources.`,
    children: [
      {
        id: 'sec-8-1',
        title: '8.1 Protocols & Internet',
        page: 5,
        pageLabel: 'p. 5',
        summary: 'TCP/IP, DNS, and HTTP/HTTPS.',
        excerpt: `TCP/IP supports communication; DNS translates domain names into IP addresses.`,
        children: [],
      },
      {
        id: 'sec-8-2',
        title: '8.2 Networking Metrics',
        page: 5,
        pageLabel: 'p. 5',
        summary: 'IP address, Router, Bandwidth, and Latency.',
        excerpt: `• IP Address: Identifies a device.
• Router: Forwards packets between networks.
• Protocol: Rules for communication.
• Bandwidth: Data transmission volume over time.
• Latency: Transmission delay between send and receive.`,
        children: [],
      },
    ],
  },
  {
    id: 'ch-9',
    title: 'Chapter 9: Cybersecurity',
    page: 5,
    pageLabel: 'p. 5',
    summary: 'Protecting systems, data, and networks from unauthorized access.',
    excerpt: `Cybersecurity protects computers, networks, applications, and data from unauthorized access, misuse, disruption, or damage.`,
    children: [
      {
        id: 'sec-9-1',
        title: '9.1 Security Best Practices',
        page: 5,
        pageLabel: 'p. 5',
        summary: 'Passwords, MFA, least privilege, backups, and encryption.',
        excerpt: `• Strong passwords and multi-factor authentication (MFA).
• Keep operating systems updated.
• Avoid suspicious links.
• Regular backups.
• Principle of least privilege.
• Encrypt sensitive information.`,
        children: [],
      },
    ],
  },
  {
    id: 'ch-10',
    title: 'Chapter 10: Conclusion',
    page: 5,
    pageLabel: 'p. 5',
    summary: 'Combining theory with practice: write code, test examples, and debug.',
    excerpt: `Computer Science combines mathematics, logic, creativity, and engineering. The most effective way to learn is combining theory with practice: read concepts, write code, test examples, debug errors, and build projects.`,
    children: [],
  },
]
