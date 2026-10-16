// This file acts as a temporary data utility to serve the lessons data
// to the frontend, replacing a future API call.

const lessonsData = {
  lessons: [
    {
      id: "simple",
      title: "Simple Sentences: The Foundation",
      teaching_content:
        "A simple sentence contains one independent clause. It expresses a single complete thought. Example: 'The cat slept.'",
      prerequisite_id: null,
      practice: {
        level_1_mcq: [
          {
            id: 101,
            question: "Which of the following is a simple sentence?",
            options: [
              "A. I ran and she walked, and the sun set quickly.",
              "B. Because it was raining, I took a coat.",
              "C. The sun is shining.",
              "D. I ran and she walked.",
            ],
            answer: "C",
          },
        ],
        level_2_jumbled: [
          {
            id: 102,
            parts: ["my homework", "I finished", "quickly"],
            correct_sequence: ["I finished", "my homework", "quickly."],
          },
          {
            id: 104,
            parts: ["running", "The", "dog", "excitedly", "was"],
            correct_sequence: ["The", "dog", "was", "running", "excitedly."],
          },
          {
            id: 105,
            parts: ["always", "early", "arrives", "She"],
            correct_sequence: ["She", "always", "arrives", "early."],
          },
        ],
        level_3_prompt: [
          {
            id: 103,
            prompt_text:
              "Write one clear simple sentence describing a moment of surprise.",
          },
        ],
      },
    },
    {
      id: "compound",
      title: "Compound Sentences: Combining Thoughts",
      teaching_content:
        "A compound sentence joins two or more independent clauses, usually with a coordinating conjunction (FANBOYS: For, And, Nor, But, Or, Yet, So) or a semicolon. Example: 'The cat slept, and the dog played.'",
      prerequisite_id: "simple",
      practice: {
        level_1_mcq: [
          {
            id: 201,
            question:
              "Which sentence correctly uses a coordinating conjunction to form a compound sentence?",
            options: [
              "A. Although it was cold, I still went for a walk.",
              "B. I like tea, but she prefers coffee.",
              "C. The student studied hard for the test which was tomorrow.",
              "D. Running quickly and jumping high, the athlete won.",
            ],
            answer: "B",
          },
        ],
        level_2_jumbled: [
          {
            id: 202,
            parts: ["the train", "I missed", "so", "I was late", ","],
            correct_sequence: [
              "I missed",
              "the train",
              ",",
              "so",
              "I was late",
              ".",
            ],
          },
          {
            id: 204,
            parts: [
              "finished",
              "his lunch",
              "or",
              "he did not",
              "She",
              "cooked",
              "it",
              ",",
            ],
            correct_sequence: [
              "She",
              "cooked",
              "his lunch",
              ",",
              "or",
              "he did not",
              "finish",
              "it",
              ".",
            ],
          },
          {
            id: 205,
            parts: [
              "we stayed",
              "at home",
              "but",
              "The rain",
              "was heavy",
              ",",
            ],
            correct_sequence: [
              "The rain",
              "was heavy",
              ",",
              "but",
              "we stayed",
              "at home",
              ".",
            ],
          },
        ],
        level_3_prompt: [
          {
            id: 203,
            prompt_text:
              "Using a coordinating conjunction (for example, 'and' or 'but'), write a compound sentence about two different foods you enjoy.",
          },
        ],
      },
    },
    {
      id: "complex",
      title: "Complex Sentences: Subordination",
      teaching_content:
        "A complex sentence contains one independent clause and at least one dependent clause. The clauses are connected using subordinating conjunctions (e.g., because, although, since) or relative pronouns. Example: 'Because the cat was hungry, it meowed.'",
      prerequisite_id: "compound",
      practice: {
        level_1_mcq: [],
        level_2_jumbled: [],
        level_3_prompt: [
          {
            id: 303,
            prompt_text:
              "Using the subordinating conjunction 'although,' write a complex sentence about a difficult task you completed.",
          },
        ],
      },
    },
  ],
};

// Export the data structure so it can be imported by LessonList.jsx and LessonDetail.jsx
export const getLessons = () => {
  return lessonsData;
};
