/**
 * QuizCard - 练习题卡片（严格按照原始设计）
 */
import { useState } from 'react'

interface QuizQuestion {
  question_number: number
  question_text: string
  question_type: string
  options?: Array<{ key: string; text: string }>
  correct_answer: string | string[]
  explanation: string
}

interface QuizCardProps {
  data: {
    quiz_set?: {
      title: string
      topic: string
      difficulty: string
      questions: QuizQuestion[]
    }
  }
}

export function QuizCard({ data }: QuizCardProps) {
  const quizSet = data.quiz_set
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [score, setScore] = useState(0)

  if (!quizSet || !quizSet.questions || quizSet.questions.length === 0) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <p className="text-gray-500">暂无练习题</p>
      </div>
    )
  }

  const question = quizSet.questions[currentQuestion]
  const totalQuestions = quizSet.questions.length
  const isCorrect = selectedAnswer === question.correct_answer
  const progress = ((currentQuestion + 1) / totalQuestions) * 100

  const handleSubmit = () => {
    if (selectedAnswer && !isSubmitted) {
      setIsSubmitted(true)
      if (isCorrect) {
        setScore(score + 1)
      }
    }
  }

  const handleNext = () => {
    if (currentQuestion < totalQuestions - 1) {
      setCurrentQuestion(currentQuestion + 1)
      setSelectedAnswer(null)
      setIsSubmitted(false)
    }
  }

  return (
    <div className="flex flex-col gap-6 rounded-xl border border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark p-6 sm:p-8 shadow-sm">
      {/* Header with Progress */}
      <div className="flex flex-col gap-3">
        <div className="flex gap-6 justify-between">
          <p className="text-primary text-base font-medium leading-normal">{quizSet.title}</p>
        </div>
        <div className="rounded bg-slate-200 dark:bg-slate-700">
          <div className="h-2 rounded bg-primary" style={{ width: `${progress}%` }} />
        </div>
        <p className="text-slate-500 dark:text-slate-400 text-sm font-normal leading-normal">
          Question {currentQuestion + 1} of {totalQuestions}
        </p>
      </div>

      {/* Divider */}
      <div className="border-t border-border-light dark:border-border-dark" />

      {/* Question */}
      <h1 className="text-text-light-primary dark:text-text-dark-primary tracking-tight text-2xl md:text-3xl font-bold leading-tight text-left">
        {question.question_text}
      </h1>

      {/* Options */}
      {question.options && (
        <div 
          className="flex flex-col gap-3"
          style={{
            '--radio-dot-svg': 'url(\'data:image/svg+xml,%3csvg viewBox=%270 0 16 16%27 fill=%27rgb(19,127,236)%27 xmlns=%27http://www.w3.org/2000/svg%27%3e%3ccircle cx=%278%27 cy=%278%27 r=%273%27/%3e%3c/svg%3e\')'
          } as React.CSSProperties}
        >
          {question.options.map((option) => {
            const isSelected = selectedAnswer === option.key
            const isThisCorrect = option.key === question.correct_answer
            
            let labelClasses = 'flex items-center gap-4 rounded-lg border border-solid border-border-light dark:border-border-dark p-4 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/50'
            let radioClasses = 'h-5 w-5 border-2 border-border-light dark:border-border-dark bg-transparent text-transparent checked:border-primary checked:bg-[image:--radio-dot-svg] focus:outline-none focus:ring-0 focus:ring-offset-0 checked:focus:border-primary'
            
            if (isSubmitted) {
              if (isThisCorrect) {
                labelClasses = 'flex items-center gap-4 rounded-lg border-2 border-solid border-success bg-success/10 p-4 cursor-default'
                radioClasses = 'h-5 w-5 border-2 border-success bg-transparent text-transparent checked:border-success checked:bg-[image:--radio-dot-svg] focus:outline-none focus:ring-0 focus:ring-offset-0'
              } else if (isSelected) {
                labelClasses = 'flex items-center gap-4 rounded-lg border-2 border-solid border-error bg-error/10 p-4 cursor-default'
                radioClasses = 'h-5 w-5 border-2 border-error bg-transparent text-transparent checked:border-error checked:bg-[image:--radio-dot-svg] focus:outline-none focus:ring-0 focus:ring-offset-0'
              } else {
                labelClasses += ' opacity-60 cursor-default'
              }
            } else {
              labelClasses += ' has-[:checked]:border-primary has-[:checked]:bg-primary/10 dark:has-[:checked]:bg-primary/20'
            }

            return (
              <label key={option.key} className={labelClasses}>
                <input
                  className={radioClasses}
                  name={`quiz-${currentQuestion}`}
                  type="radio"
                  checked={isSelected}
                  onChange={() => !isSubmitted && setSelectedAnswer(option.key)}
                  disabled={isSubmitted}
                />
                <div className="flex grow items-center justify-between">
                  <p className="text-text-light-primary dark:text-text-dark-primary text-sm font-medium leading-normal">
                    {option.text}
                  </p>
                  {isSubmitted && isThisCorrect && (
                    <span className="material-symbols-outlined text-success">check_circle</span>
                  )}
                  {isSubmitted && isSelected && !isThisCorrect && (
                    <span className="material-symbols-outlined text-error">cancel</span>
                  )}
                </div>
              </label>
            )
          })}
        </div>
      )}

      {/* Explanation (shown after submission) */}
      {isSubmitted && (
        <div className="flex flex-col gap-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 p-4 mt-2">
          <h3 className="text-lg font-bold text-text-light-primary dark:text-text-dark-primary">Explanation</h3>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            {question.explanation}
          </p>
        </div>
      )}

      {/* Action Button */}
      <div className="flex pt-4">
        {!isSubmitted ? (
          <button
            className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-5 flex-1 bg-primary text-slate-50 text-base font-bold leading-normal tracking-[0.015em] hover:bg-primary/90 disabled:bg-slate-300 dark:disabled:bg-slate-600 disabled:cursor-not-allowed"
            onClick={handleSubmit}
            disabled={!selectedAnswer}
          >
            <span className="truncate">提交</span>
          </button>
        ) : currentQuestion < totalQuestions - 1 ? (
          <button
            className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-5 flex-1 bg-primary text-slate-50 text-base font-bold leading-normal tracking-[0.015em] hover:bg-primary/90"
            onClick={handleNext}
          >
            <span className="truncate">下一题</span>
          </button>
        ) : (
          <div className="flex-1 text-center py-3">
            <p className="text-lg font-semibold text-text-light-primary dark:text-text-dark-primary">
              完成！得分: {score} / {totalQuestions}
            </p>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              正确率: {Math.round((score / totalQuestions) * 100)}%
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
