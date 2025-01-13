import { defineStore } from 'pinia';
import {
  fetchAllCampaigns, createCampaign, updateCampaign, deleteCampaign, getCampaign, 
   startCampaign, endCampaign, requestToJoinCampaign, sendMessage, getChatMessages, respondToJoinRequest, sendChatRequest, updateChatRequestStatus,searchCampaigns, markTaskAsCompleted, getCampaignTaskData, approveRejectTask, sendCampaignRequestToInfluencer, getFreshBrandCampaigns
} from '../../services/campaignService';

export const useCampaignsStore = defineStore('campaigns', {
  state: () => ({
    campaigns: [],         // Centralized campaigns data
    currentCampaign: null,  // Currently viewed/edited campaign
    // campaignRequests: [],   // Requests from influencers for a specific campaign
    chatMessages: [],
    campaignTasks: [],
    freshbrandCampaignsList: [], // brandCampaigns retrieved fresh
  }),

  getters: {
    brandCampaigns: (state) => (userId) => {
      console.log(state.campaigns)
      return state.campaigns.filter(campaign => campaign?.sponsor_id === userId);
    },
    inactiveBCampaigns: (state) => (userId) => {
      console.log(state.campaigns)
      return state.campaigns.filter(campaign => campaign?.sponsor_id === userId && campaign?.status=='inactive');
    },
    allCampaigns: (state) => {
      console.log(state.campaigns)
      return state.campaigns.filter(campaign => campaign?.visibility === "public");
    },
    campaignById: (state) => {
      return (id) => state.campaigns.find(campaign => campaign?.id === id);
    },
    campaignRequests: (state) => (userId) => {
      // Get all campaigns where the provided user is the sponsor
      const sponsoredCampaigns = state.brandCampaigns(userId);
  
      // Use flatMap to simplify the process of collecting requests
      return sponsoredCampaigns.flatMap(campaign => 
        (campaign?.influencers || []).map(influencer => ({
          campaignId: campaign.id,
          influencerId: influencer.influencer_id,
          influencerName: influencer.influencer_name,
          status: influencer.status,
          paymentAmount: influencer.payment_amount,
          participationDate: influencer.participation_date,
          influencerFeedback: influencer.influencer_feedback,
          requested: influencer.requested,
          chatRequest: influencer.chat_request,
        }))
      );
    },
  },

  actions: {
    // --- General Actions ---

    updateCampaignInStore(updatedCampaign) {
      const index = this.campaigns.findIndex(campaign => campaign.id === updatedCampaign.id);
      if (index !== -1) {
        // Replace the existing campaign
        this.campaigns[index] = updatedCampaign;
      } else {
        // Add as a new campaign if not found
        this.campaigns.push(updatedCampaign);
      }
    },

   
    // async getFreshbrandCampaignDetails(){
    //   try {
    //     const response = await getFreshBrandCampaigns();
    //     this.freshbrandCampaignsList = response.data.campaigns
    //   }
    //   catch(error){
    //     console.error(error);
    //   }
    // },

    async loadCampaigns(userId) {
      try {
        const response = await fetchAllCampaigns(userId);
        console.log(response.data.campaigns)
        this.campaigns = response.data.campaigns; // Unwrap the "campaigns" array
        console.log(this.campaigns)
      } catch (error) {
        console.error('Failed to load campaigns:', error);
      }
    },
    async searchCampaigns(filters) {
      try {
        const response = await searchCampaigns(filters); // Assume this is your backend call
        return response.data.campaigns || [];  // Default to empty array if no data
      } catch (error) {
        console.error("Failed to fetch campaigns:", error);
        return [];  // Fallback to empty array on error
      }
    },
    
    //---------------------------------------------------------------------------------------------------------------

    async getCampaignDetails(campaignId) {
      try {
        const response = await getCampaign(campaignId);
        this.currentCampaign = response.data; // Unwrap the "campaign" object
        return this.currentCampaign
      } catch (error) {
        console.error('Failed to fetch campaign:', error);
        throw error;
      }
    },
    
    //wrapper for getCampaigndetails which checks for cases where we have campaign present in the store.
    async retrieveCampaignById(campaignId) {
      // Check if the campaign is already in the state
      const campaign = this.campaignById(campaignId);
      console.log('returning campaign by id', campaign)
      if (campaign) {
        this.currentCampaign = campaign; // Use existing campaign data
        return campaign;
      } else {
        // If not found, fetch it from the server
        await this.getCampaignDetails(campaignId);
        return this.currentCampaign;
      }
    },
    async fetchAndUpdateCampaignById(campaignId) {
      try {
        // Fetch campaign details from the server
        const response = await getCampaign(campaignId);
        const campaignData = response.data;
    
        // Find the index of the campaign in the campaigns array, if it exists
        const existingIndex = this.campaigns.findIndex(campaign => campaign.id === campaignId);
        console.log('existingIndex',existingIndex)
    
        if (existingIndex !== -1) {
          // Replace the existing campaign with updated data
          this.campaigns[existingIndex] = campaignData;
        } else {
          // If the campaign is not in the list, add it
          this.campaigns.push(campaignData);
        }
    
        // Assign the fetched campaign to currentCampaign
        this.currentCampaign = campaignData;
    
        return campaignData;
      } catch (error) {
        console.error('Failed to fetch and update campaign by ID:', error);
        throw error;
      }
    },
    
  
    // async loadCampaignRequests() {
    //   try {
    //     const response = await fetchCampaignRequests();
    //     this.campaignRequests = response.data.requests;
    //   } catch (error) {
    //     console.error('Failed to load campaign requests:', error);
    //   }
    // },

    // --- Brand-specific Actions ---
    async createCampaign(campaignData) {
      try {
        const response = await createCampaign(campaignData);
        this.campaigns.push(response.data.newCampaign);
        this.currentCampaign = response.data.newCampaign;
      } catch (error) {
        console.error('Failed to create campaign:', error);
        throw error;
      }
    },

    async updateCampaign(campaignId, updatedData) {
      try {
        await updateCampaign(campaignId, updatedData);
        await this.fetchAndUpdateCampaignById(campaignId);  // Reload campaigns after updating
      } catch (error) {
        console.error('Failed to update campaign:', error);
        throw error;
      }
    },

    async deleteCampaign(campaignId) {
      try {
        // Call the API to delete the campaign
        await deleteCampaign(campaignId);
    
        // Remove the campaign from the store
        this.campaigns = this.campaigns.filter(campaign => campaign.id !== campaignId);
    
        // Optionally, reset currentCampaign if it's the one being deleted
        if (this.currentCampaign?.id === campaignId) {
          this.currentCampaign = null;
        }
    
        console.log(`Campaign with ID ${campaignId} deleted successfully.`);
      } catch (error) {
        console.error('Failed to delete campaign:', error);
        throw error;
      }
    },    

    async startCampaign(campaignId){
      try {
        await startCampaign(campaignId);
        await this.fetchAndUpdateCampaignById(campaignId);
      }
      catch (error) {
        console.error('Failed to start campaign:', error);
        throw error;
      }
    },
    async endCampaign(campaignId){
      try {
        await endCampaign(campaignId);
        await this.fetchAndUpdateCampaignById(campaignId);
      }
      catch (error) {
        console.error('Failed to end campaign:', error);
        throw error;
      }
    },


    // request and response to join campaigns.

    async respondToJoinRequest(influencerId, respondData, campaignId) {
      try {
        await respondToJoinRequest(influencerId,campaignId, respondData);
        await this.fetchAndUpdateCampaignById(campaignId); // Reload campaign requests for the brand
      } catch (error) {
        console.error('Failed to respond to join request:', error);
        throw error;
      }
    },
    
    async submitCampaignRequest(campaignId) {
      try {
        const response = await requestToJoinCampaign(campaignId);
        return response;
      } catch (error) {
        console.error('Failed to submit campaign request:', error);
        throw error;
      }
    },

    // sending and loading messages

    async sendCampaignMessage(campaignId, messageData, influencerId) {
      try {
        await sendMessage(campaignId, messageData, influencerId);
        await this.loadCampaignMessages(campaignId, influencerId);
      } catch (error) {
        console.error('Failed to send message:', error);
        throw error;
      }
    },


    async loadCampaignMessages(campaignId, influencerId) {
      try {
        const response = await getChatMessages(campaignId, influencerId);
        this.chatMessages = response.data;
        console.log(this.chatMessages)
      } catch (error) {
        console.error('Failed to load chat messages:', error);
      }
    },

    async sendChatRequest(campaignId) {
      try {
        const response = await sendChatRequest(campaignId);
        await this.fetchAndUpdateCampaignById(campaignId);
        return response; // Return the response data for further handling
      } catch (error) {
        console.error('Failed to send chat request:', error);
        throw error; // Propagate error for handling in the component
      }
    },

    // Updating chat request status
    async updateChatRequestStatus(campaignId, influencerId, status) {
      try {
        const response = await updateChatRequestStatus(campaignId, influencerId, status);
        await this.fetchAndUpdateCampaignById(campaignId);
        return response; // Return the response data for further handling
      } catch (error) {
        console.error('Failed to update chat request status:', error);
        throw error; // Propagate error for handling in the component
      }
    },



    async loadCampaignTasks(campaignId) {
      try {
        const response = await getCampaignTaskData(campaignId);
        this.campaignTasks =  response.influencers || [];
        console.log(this.campaignTasks)
      } catch (error) {
        console.error('Failed to load campaign tasks:', error);
      }
    },

    async markTaskAsCompleted(taskId, campaignId) {
      try {
        await markTaskAsCompleted(taskId,campaignId);
        await this.loadCampaignTasks(this.currentCampaign.id); // Reload tasks to update status
      } catch (error) {
        console.error('Failed to mark task as completed:', error);
        throw error;
      }
    },

    async approveRejectTask(taskId, status, influencerId, feedback, campaignId) {
      try {
        await approveRejectTask(taskId, status, influencerId, feedback, campaignId);
        await this.loadCampaignTasks(this.currentCampaign.id); // Reload tasks to reflect approval/rejection
      } catch (error) {
        console.error(`Failed to ${status} task:`, error);
        throw error;
      }
    },

    async sendCampaignRequestToInfluencer(campaignId,influencerId) {
      try  {
        const response = await sendCampaignRequestToInfluencer(campaignId,influencerId);
        console.log(response)
        return response;
      } catch (error) {
        console.log('error occurred');
        throw error;
      }
    }

  },
});

export default useCampaignsStore;