// Quiz questions data
const quizData = {
  general: [
    {
      question: "What is the capital of India?",
      answers: ["Mumbai", "New Delhi", "Chennai", "Kolkata"],
      correct: 1
    },
    {
      question: "Which festival is known as the Festival of Lights?",
      answers: ["Holi", "Navratri", "Diwali", "Eid"],
      correct: 2
    }
  ],
  science: [
    {
      question: "What planet is known as the Red Planet?",
      answers: ["Earth", "Mars", "Jupiter", "Venus"],
      correct: 1
    },
    {
      question: "What is the boiling point of water?",
      answers: ["90°C", "100°C", "110°C", "120°C"],
      correct: 1
    }
  ],
  sports: [
    {
      question: "How many players in a football team?",
      answers: ["9", "10", "11", "12"],
      correct: 2
    },
    {
      question: "Which country won the 2011 Cricket World Cup?",
      answers: ["Australia", "England", "India", "South Africa"],
      correct: 2
    }
  ]
};

// Get quiz category from URL
const params = new URLSearchParams(window.location.search);
const category = params.get("category");
const questions = quizData[category] || [];

// Set quiz title
document.getElementById("quiz-title").textContent = `${category ? category.toUpperCase() : "QUIZ"}`;

// DOM elements
const questionEl = document.getElementById("question");
const answersEl = document.getElementById("answers");
const resultBox = document.getElementById("result-box");
const scoreEl = document.getElementById("score");
const quizBox = document.getElementById("quiz-box");
let timerEl = document.getElementById("timer");

// Timer variables
let currentIndex = 0;
let score = 0;
let timeLeft = 15;
let timerId;

function loadQuestion() {
  if (currentIndex >= questions.length) {
    return showResult();
  }

  // Reset and start timer
  clearInterval(timerId);
  timeLeft = 15;
  timerEl.textContent = `Time Left: ${timeLeft}s`;
  timerEl.style.display = "block";
  quizBox.classList.remove("hide");
  resultBox.classList.add("hide");

  const current = questions[currentIndex];
  questionEl.textContent = current.question;
  answersEl.innerHTML = "";

  current.answers.forEach((answer, index) => {
    const button = document.createElement("button");
    button.textContent = answer;
    button.addEventListener("click", () => checkAnswer(index));
    answersEl.appendChild(button);
  });

  timerId = setInterval(countdown, 1000);
}

function countdown() {
  timeLeft--;
  timerEl.textContent = `Time Left: ${timeLeft}s`;

  if (timeLeft <= 0) {
    clearInterval(timerId);
    currentIndex++;
    loadQuestion();
  }
}

function checkAnswer(selectedIndex) {
  clearInterval(timerId);
  const correctIndex = questions[currentIndex].correct;
  if (selectedIndex === correctIndex) {
    score++;
  }
  currentIndex++;
  loadQuestion();
}

function showResult() {
  clearInterval(timerId);
  quizBox.classList.add("hide");
  timerEl.style.display = "none";
  resultBox.classList.remove("hide");
  scoreEl.textContent = `${score} / ${questions.length}`;

  // Save score to localStorage
  localStorage.setItem("latestScore", `${score} / ${questions.length}`);

  // Optional redirect after delay (commented)
  // setTimeout(() => {
  //   window.location.href = "home.html";
  // }, 5000);
}

// Start quiz
loadQuestion();
