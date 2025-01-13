<template>
    <section v-if="authStore && campaignsStore">

      <!-- Chat Request Section for Influencer -->
    <div v-if="authStore.userProfile.role === 'influencer'" :style="{ opacity: openchatvalue ? 0.2 : 1 }">
      <!-- <p>{{ filteredInfluencer }}</p> -->
        <div v-if="authStore.userProfile.role === 'influencer' && (filteredInfluencer || !filteredInfluencer|| filteredInfluencer.chat_request === 'pending' ||  filteredInfluencer.chat_request === 'null')" class="w-100 d-flex align-items-center justify-content-center">
        <button class="chat_request-btn mt-2 mb-2" @click="sendChatRequest" :disabled="(filteredInfluencer && (disableButton || filteredInfluencer.chat_request === 'pending' || filteredInfluencer.chat_request === 'rejected' )) || chatRequestSent || disableButton">
          {{(filteredInfluencer && (filteredInfluencer.chat_request === 'pending' || filteredInfluencer.chat_request === 'rejected' || disableButton) || disableButton || chatRequestSent)?'Chat Requested':'Send Chat Request'}}
        </button>
      </div>
      <div v-if="filteredInfluencer && filteredInfluencer && filteredInfluencer.chat_request === 'rejected'" class="alert alert-danger">
        Your chat request has been rejected. You can no longer chat.
      </div>
      <div v-else-if="authStore.userProfile.role==='influencer' && filteredInfluencer && filteredInfluencer.chat_request==='accepted'" class="d-flex flex-column">
        <div class="d-flex align-items-center justify-contnt-center alert alert-success gap-5">
            <h6>Your request got accepted, now you can chat!!!</h6>
            <button @click="openChat(authStore.userProfile.id)">Open chat</button>
        </div>
          <div class="d-flex w-100 align-items-center justify-content-center">
        <button class="text-wrap text-dark" disabled>You can talk to campaign owners and negotiate various aspects of the campaign. Be respectful in the chat. Raise your concerns and have a nice time.</button>
      </div>
      </div>


    </div>


  
      <!-- Sponsor Section -->
      <div v-if="authStore.userProfile.id === campaign.sponsor_id" class="profiles" :style="{ opacity: openchatvalue ? 0.2 : 1 }">
        <div v-for="influencer in campaign.influencers" :key="influencer.influencer_id" class="individual-section d-flex align-items-center justify-content-between gap-2 flex-wrap">
            <button>
                <router-link class="nav-link" :to="`/user/user-profile/${influencer.influencer_id}`">{{ influencer.influencer_name }}</router-link>
            </button>
            <p v-if="requestStatus[influencer.influencer_id]?.disableAccept" class="text-success mt-2">
            Request Accepted
            </p>
          <p v-else-if="requestStatus[influencer.influencer_id]?.disableReject" class="text-danger mt-2">Request Rejected</p>
          <!-- <p v-else :class="['mt-2', influencer.chat_request==='accepted'?'alert alert-success':'alert alert-danger','fw-bold']">{{ influencer.chat_request==='null'?'No chat request sent':''}}</p> -->
          <!-- Button to Accept Chat Request -->
          <button
          v-if="(influencer.chat_request === 'pending' || influencer.chat_request === 'rejected') || requestStatus[influencer.influencer_id]?.disableReject"
          @click="updateChatRequestStatus(campaign.id, influencer.influencer_id, 'accepted')"
          class="btn-success"
          :disabled="requestStatus[influencer.influencer_id]?.disableAccept">
          Accept
        </button>

        <button
          v-if="(influencer.chat_request === 'pending' || influencer.chat_request === 'accepted') || requestStatus[influencer.influencer_id]?.disableAccept"
          @click="updateChatRequestStatus(campaign.id, influencer.influencer_id, 'rejected')"
          class="btn-danger"
          :disabled="requestStatus[influencer.influencer_id]?.disableReject">
          Reject
        </button>

        <!-- Chat Button -->
        <button
          v-if="influencer.chat_request === 'accepted' || requestStatus[influencer.influencer_id]?.disableAccept"
          @click="openChat(influencer.influencer_id)"
          class="btn-warning p-2"
          :disabled="requestStatus[influencer.influencer_id]?.disableChat">
          Chat
        </button>
          <div v-if="campaign.influencers.length===0 || influencer.chat_request==='null'" class="p-2 d-flex align-items-center justify-content-center">
              <p class="alert alert-warning text-secondary fs-6">No Requests from {{ influencer.influencer_name }} Yet</p>
          </div>
        </div>
        <div v-if="campaign.influencers.length===0" class="p-2 d-flex align-items-center justify-content-center">
            <p class="fw-bold fs-6">No Requests from Influencers Yet</p>
        </div>
      </div>



            <!-- Chat Section -->
      <div v-if="(filteredInfluencer && (filteredInfluencer.chat_request === 'accepted' || authStore.userProfile.id === campaign.sponsor_id) && openchatvalue) || (authStore.userProfile.id === campaign.sponsor_id && openchatvalue)" class="chat-container">
        <div class="chat-header">
          <h3></h3>
          <button @click="exitChat">Exit Chat</button>
        </div>
  
        <!-- Chat Messages -->
        <div class="chat-messages hide-scrollbar" ref="messagesContainer">
            <div v-for="message in chatMessages.messages" :key="message.id" :class="getMessageClass(message.sender_type)" class="message-item">                
              <p><strong>{{ message.sender_type==='sponsor'?'':influencerName+' :' }}</strong> {{ message.content }}</p>
                <!-- <span class="message-time">{{ formatDate(message.timestamp) }}</span> -->
                </div>
        </div>
  
        <!-- Send Message Input -->
        <div class="chat-input">
          <input
            type="text"
            v-model="newMessage"
            placeholder="Type your message..."
            @keyup.enter="sendMessage"
          />
          <button @click="sendMessage">Send</button>
        </div>
      </div>
    </section>
  </template>
  
  <script>
  import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
  import { useCampaignsStore } from '../../../store';
  import { useAuthStore } from '../../../store';
  import { fetchUserProfileById } from '../../../services/userservice';
  
  export default {
    name: 'CampaignChat',
    props: {
      campaign: {
        type: Object,
        required: true,
      },
    },
    setup(props) {
      const campaignsStore = useCampaignsStore();
      const newMessage = ref('');
      const authStore = useAuthStore();
      const messagesContainer = ref(null);
      const selectedInfluencerId = ref(null);
      const openchatvalue = ref(false);
      const requestStatus = ref({});
      const influencerName = ref('');
      const pollingInterval = ref(null);
      const disableButton = computed(()=>{return (chatRequestSent.value || localStorage.getItem(`chat_request_sent:${props.campaign.id}`) === 'true');})
      const chatRequestSent = ref(false);
      const chatMessages = computed(() => campaignsStore.chatMessages);
  
      const filteredInfluencer = computed(() => {
        return props.campaign.influencers.find(
          (influencer) => influencer.influencer_id === authStore.userProfile.id
        );
      });
  
      // Send a new message
      const sendMessage = async () => {
        if (newMessage.value.trim() !== '') {
          const messageData = { content: newMessage.value };
          await campaignsStore.sendCampaignMessage(props.campaign.id, messageData, selectedInfluencerId.value);
          newMessage.value = '';
          scrollToBottom();
        }
      };
  
      const loadChatMessages = async (campaignId, influencerId) => {
        await campaignsStore.loadCampaignMessages(campaignId, influencerId);
      };
  
      const openChat = async (influencerId) => {
        openchatvalue.value=true;
        selectedInfluencerId.value = influencerId;
        const data = await fetchUserProfileById(influencerId);
        console.log(data)
        influencerName.value = data.first_name +' '+data.last_name;
        await loadChatMessages(props.campaign.id, influencerId);
        // campaignsStore.subscribeToChat(props.campaign.id, influencerId);
        scrollToBottom();
        startPolling();
      };
  
      // Format message timestamp
      const formatDate = (timestamp) => new Date(timestamp).toLocaleTimeString();
  
      // Scroll to bottom of messages container
      const scrollToBottom = () => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
      };

      const startPolling = () => {
      if (pollingInterval.value) return; // Prevent multiple intervals
      pollingInterval.value = setInterval(async () => {
        await loadChatMessages(props.campaign.id, selectedInfluencerId.value);
      }, 20000); // Poll every 10 seconds
    };

    const stopPolling = () => {
      if (pollingInterval.value) {
        clearInterval(pollingInterval.value);
        pollingInterval.value = null;
      }
    };
    onMounted(()=>{
      localStorage.removeItem(`chat_request_sent:${props.campaign.id}`,true)
    })

  
      // Watch for new messages and scroll to the bottom
      watch(() => campaignsStore.chatMessages, scrollToBottom);
  
      // Exit chat function
      const exitChat = () => {
        console.log('Exiting chat');
        openchatvalue.value=false;
        stopPolling();
        // Implement additional chat exit logic here if needed
      };
  
      // Sending and accepting requests
      const sendChatRequest = async () => {
        localStorage.setItem(`chat_request_sent:${props.campaign.id}`,true)
        chatRequestSent.value = true;
        await campaignsStore.sendChatRequest(props.campaign.id);
      };
      // onMounted(()=>{
      //   localStorage.removeItem('chat_request_sent:1');
      // })
      
      const updateChatRequestStatus = async (campaignId, influencerId, status) => {
      try {
        await campaignsStore.updateChatRequestStatus(campaignId, influencerId, status);
        if (!requestStatus.value[influencerId]) requestStatus.value[influencerId] = {};

        if (status === 'accepted') {
          requestStatus.value[influencerId].disableAccept = true;
          requestStatus.value[influencerId].disableReject = false;
          requestStatus.value[influencerId].disableChat = false;
        } else if (status === 'rejected') {
          requestStatus.value[influencerId].disableAccept = false;
          requestStatus.value[influencerId].disableReject = true;
          requestStatus.value[influencerId].disableChat = true;
        }
      } catch (error) {
        console.error('Failed to update chat request status:', error);
      }
    };


      const getMessageClass = (senderType) => {
      // Determine the message alignment based on user role and sender type
      if (authStore.userProfile.role === 'influencer' && senderType === 'influencer') {
        return 'message-item-influencer'; // Align right
      } else if (authStore.userProfile.role === 'brand' && senderType === 'sponsor') {
        return 'message-item-sponsor'; // Align right
      } else {
        return 'message-item-other'; // Align left
      }
    };

    // onMounted(() => {
    //         campaignsStore.initializeSocketListeners();
    //     });
    // onMounted(() => {
    //   // Subscribe to chat messages for the current campaign and influencer
      
    // });

    // onUnmounted(() => {
    //   // Unsubscribe when the component unmounts to clean up the connection
    //   campaignsStore.unsubscribeFromChat();
    // });
      return {
        newMessage,
        chatMessages,
        sendMessage,
        exitChat,
        messagesContainer,
        formatDate,
        filteredInfluencer,
        sendChatRequest,
        authStore,
        campaignsStore,
        updateChatRequestStatus,
        openChat,
        selectedInfluencerId,
        openchatvalue,
        getMessageClass,
        requestStatus,
        influencerName,
        disableButton,
        chatRequestSent
      };
    },
  };
  </script>
  
  
  <style scoped>
  .chat-container {
    display: flex;
    flex-direction: column;
    height: 30rem;
    margin: -25rem -1rem;
    border: 1px solid #ccc;
    border-radius: 5px;
    overflow: hidden;
    position: relative;
    background-color: #10845f00;
    z-index: 2;
    background-color: #5454545d;
  }
  
  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background-color: #ffcc74;
    border-bottom: 1px solid #ddd;
  }
  
  .chat-messages {
    flex: 1;
    padding: 10px;
    overflow-y: auto;
  }
  
  .message-item {
    margin-bottom: 10px;
  }
  
  .message-time {
    display: block;
    font-size: 0.8em;
    color: #888;
  }
  
  .chat-input {
    display: flex;
    padding: 1rem;
  }
  .hide-scrollbar::-webkit-scrollbar {
    display: none; /* Safari and Chrome */
}
.hide-scrollbar{
  background-color: 1px solid black;
}

  .chat-input input {
    flex: 1;
    padding: 8px;
    margin-right: 5px;
    border: 1px solid #cccccc99;
    border-radius: 0.5rem;
  }
  
  .chat-input button {
    padding: 8px 12px;
    background-color: #ffde96;
    color: rgb(255, 255, 255);
    border: none;
    border-radius: 3px;
    cursor: pointer;
  }
  
  .chat-input button:hover {
    background-color: #ff195e;
  }


  .message-item-influencer {
  text-align: right; /* Align influencer messages to the right */
  background-color: #ff8258ab; /* Optional: background color for influencer messages */
  border: 0.1px solid rgba(255, 255, 255, 0);
  border-radius: 1rem;
  padding: 0.5rem;
  box-shadow: 2px 2px 0.5rem rgba(104, 104, 104, 0.73);
}

.message-item-sponsor {
  text-align: right; /* Align influencer messages to the right */
  background-color: #ffb7529b; /* Optional: background color for influencer messages */
  border: 0.1px solid rgba(255, 255, 255, 0);
  border-radius: 1rem;
  padding: 0.5rem;
  box-shadow: 2px 2px 0.5rem rgba(104, 104, 104, 0.73);
}

.message-item-other {
  text-align: left; /* Align influencer messages to the right */
  background-color: #ff8694aa; /* Optional: background color for influencer messages */
  border: 0.1px solid rgba(255, 255, 255, 0);
  border-radius: 1rem;
  padding: 0.5rem;
  box-shadow: 2px 2px 0.5rem rgba(104, 104, 104, 0.73);
}

.profiles{
    background-color: #ffddb125;
    display: flex;
    flex-direction: column;
    border: 2px solid rgb(235, 235, 235);
    border-radius: 1rem;
    padding: 1rem 1rem;
    font-size: small;
    gap: 2rem;
    align-items: start;
    justify-content: space-between;
}
.individual-section{
  background-color: #ffdabc5e;
  padding: 1rem;
  width: 100%;
  border: 1px solid aliceblue;
  border-radius: 0.5rem;
}

.chat_request-btn{
  width: 10rem;
  background-color: #ffa35dd4;
  font-size: small;
  text-wrap: wrap;
}
.chat_request-btn:hover{
 padding: none;
 border: none;
 color: #fbfbfb;
 box-shadow: none;
 background-color: #ffcc74;
}
</style>
  