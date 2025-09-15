// Like functionality with IP-based restriction using localStorage
function toggleLike(button) {
  const postId = button.getAttribute('data-post-id');
  const storageKey = 'liked_posts';
  const countKey = 'like_count_' + postId;
  
  console.log('Toggle like for postId:', postId);
  
  // Get existing liked posts from localStorage
  let likedPosts = JSON.parse(localStorage.getItem(storageKey) || '[]');
  let currentCount = parseInt(localStorage.getItem(countKey) || '0');
  
  console.log('Current liked posts:', likedPosts);
  console.log('Current count:', currentCount);
  
  const heartIcon = button.querySelector('.heart-icon');
  const countDisplay = button.querySelector('.like-count');
  
  // Check if this post is already liked
  const isAlreadyLiked = likedPosts.includes(postId);
  console.log('Is already liked:', isAlreadyLiked);
  
  if (isAlreadyLiked) {
    // Unlike: Remove from liked posts and decrease count
    likedPosts = likedPosts.filter(id => id !== postId);
    currentCount = Math.max(0, currentCount - 1);
    heartIcon.textContent = '♡';
    button.classList.remove('liked');
    
    // Show feedback
    showLikeFeedback('Unliked!', false);
  } else {
    // Like: Add to liked posts and increase count
    likedPosts.push(postId);
    currentCount += 1;
    heartIcon.textContent = '♥';
    button.classList.add('liked');
    
    // Show feedback
    showLikeFeedback('Liked!', true);
  }
  
  // Update localStorage
  localStorage.setItem(storageKey, JSON.stringify(likedPosts));
  localStorage.setItem(countKey, currentCount.toString());
  
  console.log('Updated liked posts:', likedPosts);
  console.log('Updated count:', currentCount);
  
  // Update display
  countDisplay.textContent = currentCount;
  
  // Update all other buttons with the same post ID
  updateAllButtonsForPost(postId);
}

// Update all buttons for a specific post ID
function updateAllButtonsForPost(postId) {
  const storageKey = 'liked_posts';
  const countKey = 'like_count_' + postId;
  
  const likedPosts = JSON.parse(localStorage.getItem(storageKey) || '[]');
  const currentCount = parseInt(localStorage.getItem(countKey) || '0');
  const isLiked = likedPosts.includes(postId);
  
  // Find all buttons with the same post ID
  const allButtons = document.querySelectorAll(`[data-post-id="${postId}"]`);
  console.log(`Updating ${allButtons.length} buttons for postId: ${postId}`);
  
  allButtons.forEach(button => {
    const heartIcon = button.querySelector('.heart-icon');
    const countDisplay = button.querySelector('.like-count');
    
    if (isLiked) {
      heartIcon.textContent = '♥';
      button.classList.add('liked');
    } else {
      heartIcon.textContent = '♡';
      button.classList.remove('liked');
    }
    
    countDisplay.textContent = currentCount;
  });
}

// Show like/unlike feedback
function showLikeFeedback(message, isLike) {
  const feedback = document.createElement('div');
  feedback.className = 'like-feedback';
  feedback.textContent = message;
  feedback.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${isLike ? '#ff6b6b' : '#666'};
    color: white;
    padding: 10px 15px;
    border-radius: 20px;
    font-size: 14px;
    z-index: 1000;
    opacity: 0;
    transform: translateY(-10px);
    transition: all 0.3s ease;
  `;
  
  document.body.appendChild(feedback);
  
  // Animate in
  setTimeout(() => {
    feedback.style.opacity = '1';
    feedback.style.transform = 'translateY(0)';
  }, 10);
  
  // Remove after 2 seconds
  setTimeout(() => {
    feedback.style.opacity = '0';
    feedback.style.transform = 'translateY(-10px)';
    setTimeout(() => {
      document.body.removeChild(feedback);
    }, 300);
  }, 2000);
}

// Initialize like button state when page loads
document.addEventListener('DOMContentLoaded', function() {
  console.log('Like button initialization started');
  const likeButtons = document.querySelectorAll('.like-button');
  console.log('Found like buttons:', likeButtons.length);
  
  likeButtons.forEach((button, index) => {
    const postId = button.getAttribute('data-post-id');
    const storageKey = 'liked_posts';
    const countKey = 'like_count_' + postId;
    
    console.log(`Button ${index + 1}: postId = ${postId}`);
    
    // Get stored data
    const likedPosts = JSON.parse(localStorage.getItem(storageKey) || '[]');
    const currentCount = parseInt(localStorage.getItem(countKey) || '0');
    
    console.log(`Button ${index + 1}: liked posts =`, likedPosts);
    console.log(`Button ${index + 1}: current count = ${currentCount}`);
    
    // Update display
    const heartIcon = button.querySelector('.heart-icon');
    const countDisplay = button.querySelector('.like-count');
    
    if (likedPosts.includes(postId)) {
      heartIcon.textContent = '♥';
      button.classList.add('liked');
      console.log(`Button ${index + 1}: Set as liked`);
    } else {
      heartIcon.textContent = '♡';
      button.classList.remove('liked');
      console.log(`Button ${index + 1}: Set as not liked`);
    }
    
    countDisplay.textContent = currentCount;
  });
  
  console.log('Like button initialization completed');
});