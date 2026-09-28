/**
 * Practice curriculum: Quizzes, Flashcards, and Active Recall drills for document topics.
 */

export const TOPIC_PRACTICE_BANK = {
  'ch-1': {
    quiz: [
      {
        id: 'q1',
        question: 'What is the primary definition of Abstraction in Computer Science?',
        options: [
          { key: 'A', text: 'Compiling high-level code directly into binary instructions' },
          { key: 'B', text: 'Hiding unnecessary details and focusing on essential parts', isCorrect: true },
          { key: 'C', text: 'Connecting multiple computers over a network protocol' },
          { key: 'D', text: 'Reducing execution time through parallel processor threads' },
        ],
        explanation: 'Abstraction simplifies complex systems by hiding low-level details and exposing clean, conceptual interfaces.',
      },
      {
        id: 'q2',
        question: 'Which characteristic allows computational systems to execute repetitive tasks without manual intervention?',
        options: [
          { key: 'A', text: 'Automation', isCorrect: true },
          { key: 'B', text: 'Problem-solving' },
          { key: 'C', text: 'Polymorphism' },
          { key: 'D', text: 'Relational storage' },
        ],
        explanation: 'Automation executes repetitive or rule-based tasks automatically through software instructions.',
      },
      {
        id: 'q3',
        question: 'What does Efficiency primarily measure in an algorithm?',
        options: [
          { key: 'A', text: 'The number of lines in the source code file' },
          { key: 'B', text: 'Minimizing execution time, memory usage, or resources', isCorrect: true },
          { key: 'C', text: 'The quantity of comments per function' },
          { key: 'D', text: 'The type of programming language compiler used' },
        ],
        explanation: 'Efficiency assesses resource consumption—primarily CPU execution time and RAM usage.',
      },
    ],
    flashcards: [
      {
        term: 'Problem-Solving',
        definition: 'Breaking a complex challenge down into smaller, well-defined, and solvable steps.',
        context: 'Foundation of algorithmic thinking.',
      },
      {
        term: 'Abstraction',
        definition: 'Hiding unnecessary internal details to focus only on essential interfaces and behavior.',
        context: 'Key to managing complexity in software design.',
      },
      {
        term: 'Automation',
        definition: 'Allowing computers to execute sequences of instructions repeatedly without human effort.',
        context: 'Enables high scale and reproducible processing.',
      },
      {
        term: 'Efficiency',
        definition: 'Evaluating and optimizing the time and memory resources required for computation.',
        context: 'Expressed via Big-O time and space complexity.',
      },
    ],
  },

  'ch-2': {
    quiz: [
      {
        id: 'q1',
        question: 'Which area of Computer Science formalizes instructions used to program systems?',
        options: [
          { key: 'A', text: 'Operating Systems' },
          { key: 'B', text: 'Programming Languages', isCorrect: true },
          { key: 'C', text: 'Computer Networks' },
          { key: 'D', text: 'Databases' },
        ],
        explanation: 'Programming Languages define syntax and operational semantics for human-readable computational instructions.',
      },
      {
        id: 'q2',
        question: 'What is the core responsibility of an Operating System?',
        options: [
          { key: 'A', text: 'Managing hardware, memory, processes, and files', isCorrect: true },
          { key: 'B', text: 'Writing relational database queries' },
          { key: 'C', text: 'Securing packets over Wi-Fi channels only' },
          { key: 'D', text: 'Rendering 3D polygon meshes' },
        ],
        explanation: 'Operating systems manage physical resources (CPU, RAM, storage) and coordinate executing processes.',
      },
      {
        id: 'q3',
        question: 'Which subfield enables machines to perform tasks typically requiring intelligent behavior?',
        options: [
          { key: 'A', text: 'Computer Networks' },
          { key: 'B', text: 'Databases' },
          { key: 'C', text: 'Artificial Intelligence', isCorrect: true },
          { key: 'D', text: 'Cybersecurity' },
        ],
        explanation: 'AI encompasses pattern recognition, machine learning, and reasoning algorithms.',
      },
    ],
    flashcards: [
      {
        term: 'Operating Systems',
        definition: 'Core system software that mediates between hardware and application processes.',
        context: 'Handles memory scheduling, files, and I/O.',
      },
      {
        term: 'Computer Networks',
        definition: 'Interconnected devices communicating via standardized protocols (e.g. TCP/IP).',
        context: 'Enables internet, web, and distributed systems.',
      },
      {
        term: 'Databases',
        definition: 'Organized collections of structured data that support querying, updates, and persistence.',
        context: 'Managed via Database Management Systems (DBMS).',
      },
      {
        term: 'Cybersecurity',
        definition: 'Disciplines, protocols, and practices designed to safeguard systems and sensitive data.',
        context: 'Focuses on confidentiality, integrity, and availability.',
      },
    ],
  },

  'ch-3': {
    quiz: [
      {
        id: 'q1',
        question: 'What is the worst-case time complexity of Linear Search in an unsorted array of n items?',
        options: [
          { key: 'A', text: 'O(1)' },
          { key: 'B', text: 'O(log n)' },
          { key: 'C', text: 'O(n)', isCorrect: true },
          { key: 'D', text: 'O(n²)' },
        ],
        explanation: 'Linear search sequentially checks each element from beginning to end, requiring up to n comparisons.',
      },
      {
        id: 'q2',
        question: 'Which data structure follows the Last-In, First-Out (LIFO) access pattern?',
        options: [
          { key: 'A', text: 'Queue' },
          { key: 'B', text: 'Stack', isCorrect: true },
          { key: 'C', text: 'Binary Tree' },
          { key: 'D', text: 'Hash Table' },
        ],
        explanation: 'A Stack pushes and pops items from the top; the most recently added item is the first one retrieved.',
      },
      {
        id: 'q3',
        question: 'Which data structure offers fast average-case lookup using key-value pairs?',
        options: [
          { key: 'A', text: 'Hash Table', isCorrect: true },
          { key: 'B', text: 'Linked List' },
          { key: 'C', text: 'Queue' },
          { key: 'D', text: 'Stack' },
        ],
        explanation: 'Hash Tables use a hash function to map keys to bucket indices, yielding O(1) average lookup time.',
      },
    ],
    flashcards: [
      {
        term: 'Algorithm',
        definition: 'A finite, unambiguous sequence of steps designed to solve a specific problem.',
        context: 'Like a recipe: defined inputs, systematic steps, guaranteed output.',
      },
      {
        term: 'Stack (LIFO)',
        definition: 'Last-In, First-Out collection. The last element pushed is the first one popped.',
        context: 'Used in function call stacks and undo mechanisms.',
      },
      {
        term: 'Queue (FIFO)',
        definition: 'First-In, First-Out collection. The earliest inserted item is serviced first.',
        context: 'Used in task scheduling, printer queues, and event loops.',
      },
      {
        term: 'Linear Search',
        definition: 'Sequential scan of elements until the target is found. Worst-case runtime O(n).',
        context: 'Simple and requires no pre-sorting of data.',
      },
    ],
  },

  'ch-4': {
    quiz: [
      {
        id: 'q1',
        question: 'How does Software Development differ from raw Programming?',
        options: [
          { key: 'A', text: 'Software development involves no coding whatsoever' },
          { key: 'B', text: 'Development spans planning, design, testing, deployment, and maintenance', isCorrect: true },
          { key: 'C', text: 'Programming only applies to mobile devices' },
          { key: 'D', text: 'Software development is limited to writing database scripts' },
        ],
        explanation: 'Programming is code writing, while Software Engineering/Development covers the complete end-to-end lifecycle.',
      },
      {
        id: 'q2',
        question: 'Which quality characteristic ensures code can be understood and updated by other engineers?',
        options: [
          { key: 'A', text: 'Obfuscation' },
          { key: 'B', text: 'Maintainability & Readability', isCorrect: true },
          { key: 'C', text: 'Binary compression' },
          { key: 'D', text: 'Monolithic coupling' },
        ],
        explanation: 'Clean, readable code with automated tests ensures sustainable maintainability over time.',
      },
    ],
    flashcards: [
      {
        term: 'SDLC',
        definition: 'Software Development Life Cycle: Requirements -> Design -> Implementation -> Testing -> Maintenance.',
        context: 'Structured engineering methodology.',
      },
      {
        term: 'Unit Testing',
        definition: 'Automated verification that individual functions and modules behave as expected.',
        context: 'Prevents regressions during refactoring.',
      },
    ],
  },

  'ch-5': {
    quiz: [
      {
        id: 'q1',
        question: 'What is the role of RAM (Random Access Memory)?',
        options: [
          { key: 'A', text: 'Permanently saving user files across power-offs' },
          { key: 'B', text: 'Temporarily holding active data and instructions currently in use', isCorrect: true },
          { key: 'C', text: 'Executing arithmetic logic directly without a CPU' },
          { key: 'D', text: 'Connecting devices to external Wi-Fi networks' },
        ],
        explanation: 'RAM is fast, volatile storage that feeds data and instructions to the CPU during execution.',
      },
      {
        id: 'q2',
        question: 'Which component is specialized for massive parallel calculations such as matrix math and graphics rendering?',
        options: [
          { key: 'A', text: 'Hard Disk Drive (HDD)' },
          { key: 'B', text: 'GPU (Graphics Processing Unit)', isCorrect: true },
          { key: 'C', text: 'Power Supply Unit (PSU)' },
          { key: 'D', text: 'BIOS Chip' },
        ],
        explanation: 'GPUs excel at executing thousands of lightweight parallel calculations simultaneously.',
      },
    ],
    flashcards: [
      {
        term: 'CPU',
        definition: 'Central Processing Unit: the brains of the computer executing arithmetic and logic instructions.',
        context: 'Clock speeds measured in gigahertz (GHz).',
      },
      {
        term: 'RAM vs Storage',
        definition: 'RAM is volatile and fast for active execution; SSD/HDD is persistent and non-volatile.',
        context: 'Memory hierarchy balance.',
      },
    ],
  },

  'ch-6': {
    quiz: [
      {
        id: 'q1',
        question: 'What does SQL stand for and what is it primarily used for?',
        options: [
          { key: 'A', text: 'Structured Query Language: querying and managing relational databases', isCorrect: true },
          { key: 'B', text: 'System Quality Logic: debugging operating system kernels' },
          { key: 'C', text: 'Standard Queue Language: managing FIFO job orders' },
          { key: 'D', text: 'Secure Query Lock: encrypting browser storage' },
        ],
        explanation: 'SQL is the declarative domain-specific language for interacting with relational databases.',
      },
    ],
    flashcards: [
      {
        term: 'DBMS',
        definition: 'Database Management System: software suite that provides ACID guarantees, query execution, and storage.',
        context: 'Examples: PostgreSQL, SQLite, MySQL.',
      },
      {
        term: 'Relational Model',
        definition: 'Data structured into tables with typed columns, indexed rows, and foreign key relations.',
        context: 'Ensures structured consistency and relational queries.',
      },
    ],
  },
}

/**
 * Returns practice quiz, flashcards, and drills for a given node in the hierarchy.
 */
export function getPracticeForNode(node) {
  if (!node) return null

  // Check direct chapter match
  const chapterId = node.id.split('-').slice(0, 2).join('-')
  const specificData = TOPIC_PRACTICE_BANK[node.id] || TOPIC_PRACTICE_BANK[chapterId]

  if (specificData) {
    return {
      title: node.title,
      summary: node.summary,
      pageLabel: node.pageLabel || `p. ${node.page}`,
      excerpt: node.excerpt,
      quiz: specificData.quiz || [],
      flashcards: specificData.flashcards || [],
      drills: [
        { label: '📝 Quiz Me with AI', prompt: `Quiz me on "${node.title}". Ask me 1 conceptual question, wait for my response, and give me feedback.` },
        { label: '💡 Challenge Problem', prompt: `Give me a realistic scenario problem based on "${node.title}" that tests my understanding.` },
        { label: '⚡ 3 Practice Drills', prompt: `Generate 3 quick practice drills or active recall questions for "${node.title}".` },
      ],
    }
  }

  // Generative fallback for any other section or subsection
  return {
    title: node.title,
    summary: node.summary || 'Core topic concepts and practical principles.',
    pageLabel: node.pageLabel || `p. ${node.page}`,
    excerpt: node.excerpt,
    quiz: [
      {
        id: 'q-gen-1',
        question: `Which statement best reflects the key principle of "${node.title}"?`,
        options: [
          { key: 'A', text: node.summary || 'Applying methodical principles to computational problems', isCorrect: true },
          { key: 'B', text: 'Bypassing structured analysis to write non-standard scripts' },
          { key: 'C', text: 'Ignoring execution constraints and resource usage' },
          { key: 'D', text: 'Avoiding automated testing and documentation' },
        ],
        explanation: `Based on the document: ${node.summary || 'this section emphasizes structured problem solving and correct computing principles.'}`,
      },
      {
        id: 'q-gen-2',
        question: `When applying "${node.title}", what is the primary objective?`,
        options: [
          { key: 'A', text: 'Increasing system complexity unnecessarily' },
          { key: 'B', text: 'Understanding core concepts to solve practical challenges efficiently', isCorrect: true },
          { key: 'C', text: 'Restricting access to programming language compilers' },
          { key: 'D', text: 'Disabling diagnostic and error logging' },
        ],
        explanation: 'Computing topics aim to equip engineers with reliable mental models and problem-solving techniques.',
      },
    ],
    flashcards: [
      {
        term: node.title,
        definition: node.summary || node.excerpt?.slice(0, 140) || 'Key computing concept.',
        context: `Document reference: ${node.pageLabel || `p. ${node.page}`}`,
      },
      {
        term: 'Practical Application',
        definition: node.excerpt ? node.excerpt.slice(0, 180) + '...' : 'Combines foundational theory with practical engineering.',
        context: 'Hands-on practice reinforcement.',
      },
    ],
    drills: [
      { label: '📝 Quiz Me with AI', prompt: `Quiz me on "${node.title}". Ask 1 interactive question and evaluate my answer.` },
      { label: '💡 Real-World Scenario', prompt: `Provide a real-world software engineering scenario where "${node.title}" is critical.` },
      { label: '⚡ Concept Breakdown', prompt: `Break down "${node.title}" into 3 actionable rules of thumb for practical practice.` },
    ],
  }
}
