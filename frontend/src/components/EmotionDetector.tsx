import React from 'react'

interface Props {
  emotion: string
}

const EmotionDetector: React.FC<Props> = ({ emotion }) => {
  return (
    <div>
      <p>
        <strong>Emotion Detected:</strong> {emotion || 'N/A'}
      </p>
    </div>
  )
}

export default EmotionDetector
