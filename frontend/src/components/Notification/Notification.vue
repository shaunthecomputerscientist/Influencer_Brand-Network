<template>
    <h2>Notifications</h2>
    <div v-if="notifications==null || notifications.length===0 " class="d-flex align-items-center justify-content-center p-2">
      <div class="spinner-grow text-theme" role="status" v-if="notifications==null">
        <span class="sr-only">Loading...</span>
      </div>
      <div v-else-if="notifications.length==0" class="mt-3">
          <span class="alert alert-warning">No notifications yet</span>
      </div>
    </div>
    <div v-else class="notification-list hide-scrollbar">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="['notification-item', notification.is_read ?'notification-read':'notification-unread' ]"
        @mouseenter="markAsRead(notification.id)"
        @click="markAsRead(notification.id)"
        v-viewport="() => markAsRead(notification.id)"
      >
      <div class="d-flex align-items-center justify-content-center gap-4 flex-wrap">
        <div class="d-flex flex-column justify-content-center flex-wrap">
        <p class="notification-message">{{ notification.message }}</p>
        <small class="notification-timestamp">{{ formatDate(notification.created_at) }}</small>
        </div>
                
        <button v-if="!(notification.category==='flag')" class="" @click="goToCampaignDetails(notification.campaign_id)">Check out</button>

      </div>
      </div>
    </div>
  </template>
  
  <script>
  import { useAuthStore } from '../../store';
  import { onMounted, ref } from 'vue';
  import router from '../../router';
  
  export default {
    name: 'NotificationList',
  
    setup() {
      const authStore = useAuthStore();
      const notifications = ref(null);
  
      onMounted(async () => {
        // Fetch notifications when component is mounted
        await authStore.fetchNotifications(authStore.userProfile.id);
        notifications.value = authStore.notifications;
      });
  
      const markAsRead = async (notificationId) => {
        const notification = notifications.value.find(n => n.id === notificationId);
  
        if (!notification.is_read) {
            console.log('marking as read')
          // Mark this notification as read in the local state
          notification.is_read = true;
  
          // Call the store action to mark notifications as read in the backend
          await authStore.markAllNotificationsAsRead([notificationId]);
        }
      };
    const goToCampaignDetails = (campaign_id) => {
        router.push({ name: 'CampaignDetails', params: { id: campaign_id }})
    };
      const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString();
      };
  
      return {
        notifications,
        markAsRead,
        formatDate,
        goToCampaignDetails
      };
    },
  };
  </script>
  
  <style scoped>
  .notification-list {
    padding: 1rem;
    height: 20rem;
    overflow: scroll;
  }
  
  .notification-item {
    padding: 0.5rem;
    border: 1px solid #ccc;
    background-color: rgb(235, 255, 180);
    border-radius: 5px;
    margin-bottom: 0.5rem;
    cursor: pointer;
    font-size: small;
  }
  
  .notification-unread {
    background-color: #ff4d7c;
    font-weight: bold;
  }
  .notification-read {
    background-color: #f4e7d6;
    font-weight: bold;
  }
  
  .notification-message {
    margin: 0;
  }
  
  .notification-timestamp {
    font-size: 0.8rem;
    color: #666;
  

}


button{
    padding: 0.5rem;
}
button:hover{
    background-color: #95bd46;
    border: 0;

}
  </style>
  