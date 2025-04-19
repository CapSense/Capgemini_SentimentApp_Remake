
// index-feedback-handler.js
// This module contains a helper function to submit feedback (approve/reject) securely

async function handleFeedbackSubmission(type, index, feedbackItems, setStatus) {
  const item = feedbackItems[index];

  // Validate required fields
  if (!item || !item.originalText || !item.response) {
    console.error("Missing required fields for feedback submission", item);
    setStatus("Missing customer text or response. Please analyze the feedback first.");
    return;
  }

  try {
    const response = await fetch("/api/feedback", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        original_text: item.originalText,
        response_text: item.response,
        feedback: type // 'approved' or 'rejected'
      })
    });

    const result = await response.json();

    if (response.ok) {
      setStatus("Feedback saved successfully.");
    } else {
      console.error("Feedback submission error:", result);
      setStatus(result.error || "Failed to submit feedback.");
    }
  } catch (error) {
    console.error("Network or server error:", error);
    setStatus("Server error occurred. Please try again later.");
  }
}

// Example usage on Approve button click:
// handleFeedbackSubmission('approved', selectedIndex, feedbackArray, setStatusFunction);

export default handleFeedbackSubmission;
