<template>
  <div class="campaign-info">
    <header>
      <h2>Campaign Regulations</h2>
      <p class="intro-text">
        Learn about campaign progress evaluation, task management, and goal tracking mechanisms.
      </p>
    </header>

    <!-- Task Progress Section -->
    <section class="info-section">
      <h3>Task Progress</h3>
      <p class="info-description">
        <i class="fas fa-tasks"></i> 
        Campaign progress is split into two parts: **Task Progress (50%)** and **Goal Progress (50%)**. 
        Sponsors assign specific tasks to influencers, such as creating posts, videos, or other promotional content. 
        Completing all tasks guarantees **70% of the payment**, while the remaining **30%** depends on the performance metrics calculated as part of goal progress.
      </p>
    </section>

    <!-- Goal Progress Section -->
    <section class="info-section">
      <h3>Goal Progress</h3>
      <p class="info-description">
        <i class="fas fa-bullseye"></i> 
        The other **50% of campaign progress** is based on **Goal Progress**, which is further divided into two components:
      </p>
      <ul>
        <li>
          <b>Influencer Socials (70% weight):</b> 
          Tracks metrics like **likes** or **views** from posts made by influencers. For example, if a campaign has the goal of "brand awareness," it may require achieving a specific number of likes or views as determined by an algorithm. Progress is calculated as:
          <ul>
            <li>Likes Progress = (Likes Obtained ÷ Likes Target) × 100</li>
            <li>Views Progress = (Views Obtained ÷ Views Target) × 100</li>
          </ul>
          The progress is averaged across all social media platforms and posts for each influencer.
        </li>
        <li>
          <b>Brand Socials (30% weight):</b> 
          Tracks the **brand’s growth metrics**, such as gaining followers on the sponsor's social media account. If the target number of followers is achieved, it contributes **30%** to the Goal Progress.
        </li>
      </ul>
    </section>

    <!-- Example Goals Section -->
    <section class="info-section">
      <h3>Example Goals</h3>
      <p class="info-description">
        Our system defines goals based on campaign objectives, such as:
      </p>
      <ul>
        <li><b>Brand Awareness:</b> Increase visibility of the product/service (goal_id_1).</li>
        <li><b>Engagement & Community Building:</b> Foster interaction with potential customers (goal_id_2).</li>
        <li><b>Website Traffic Generation:</b> Drive traffic to the sponsor's website (goal_id_3).</li>
      </ul>
      Each goal is tracked based on the **influencer’s posts (Influencer Socials)** and **brand’s follower growth (Brand Socials)**.
    </section>

    <!-- Progress Calculation Section -->
    <section class="info-section">
      <h3>Goal Progress Calculation</h3>
      <p class="info-description">
        <i class="fas fa-calculator"></i> 
        The system calculates **Goal Progress** as follows:
      </p>
      <ul>
        <li>
          <b>Step 1:</b> Collect progress metrics from all influencers participating in the campaign. For each post:
          <ul>
            <li>If likes are tracked: <code>Likes Progress = (Likes Obtained ÷ Likes Target) × 100</code></li>
            <li>If views are tracked: <code>Views Progress = (Views Obtained ÷ Views Target) × 100</code></li>
          </ul>
        </li>
        <li>
          <b>Step 2:</b> Average the progress across all social media platforms for each influencer.
        </li>
        <li>
          <b>Step 3:</b> Average the progress of all accepted influencers. This becomes the **Influencer Socials Progress**.
        </li>
        <li>
          <b>Step 4:</b> Track the brand’s progress by calculating follower growth: 
          <code>Brand Progress = (Brand Followers Gained ÷ Brand Followers Target) × 100</code>.
        </li>
        <li>
          <b>Step 5:</b> Combine the **weighted progress**:
          <ul>
            <li><b>Influencer Socials:</b> Weighted at 70% of Goal Progress.</li>
            <li><b>Brand Socials:</b> Weighted at 30% of Goal Progress.</li>
          </ul>
        </li>
      </ul>
      The total **Goal Progress = (0.7 × Influencer Socials Progress) + (0.3 × Brand Socials Progress)**.
    </section>

    <!-- Final Progress Section -->
    <section class="info-section">
      <h3>Final Campaign Progress</h3>
      <p class="info-description">
        The total **Campaign Progress** is calculated by averaging **Task Progress** and **Goal Progress**:
        <code>Campaign Progress = 0.5 × (Task Progress + Goal Progress)</code>.
        This ensures a balance between task completion and performance-driven metrics.
      </p>
    </section>
  </div>
</template>

<script>
export default {
  name: "CampaignRegulations",
};
</script>

<style scoped>
/* Same styles from original code */
.campaign-info {
  max-width: 700px;
  margin: 0 auto;
  padding: 2rem;
  font-family: Arial, sans-serif;
  background: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

header {
  text-align: center;
  margin-bottom: 2rem;
}

header h2 {
  font-size: 2rem;
  color: #333;
}

.intro-text {
  color: #666;
  font-size: 1.1rem;
}

.info-section {
  margin-bottom: 1.5rem;
  background: #fff;
  padding: 1.2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.info-section h3 {
  font-size: 1.5rem;
  color: #3d85c6;
  margin-bottom: 0.5rem;
}

.info-description {
  font-size: 1rem;
  color: #555;
  line-height: 1.6;
}

.info-description i {
  margin-right: 0.5rem;
  color: #3d85c6;
  font-size: 1.2rem;
}

ul {
  padding-left: 1.5rem;
  margin: 0.5rem 0;
  list-style: disc;
}

li {
  margin-bottom: 0.5rem;
}
</style>