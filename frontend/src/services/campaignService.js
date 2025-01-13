import { axiosInstance, getHeaders } from './axiosInstance';
import {io} from "socket.io-client";



// const token = localStorage.getItem('access_token');
// const socket = io(import.meta.env.VITE_APP_BACKEND_URL, {
//     transports: ["websocket"],
//     withCredentials: true,
//     auth: {
//         token: `Bearer ${token}` // Pass token here as "Bearer <token>"
//     }
// });




export const fetchAllCampaigns = async (userId) => {
  return axiosInstance.get(`/campaigns/all/${userId}`, { headers: getHeaders() });
};

export const searchCampaigns = async (filters) => {
  return axiosInstance.post('/campaigns/search', filters, {headers : getHeaders()});
}

export const createCampaign = async (campaignData) => {
  return axiosInstance.post('/campaigns/create', campaignData, { headers: getHeaders() });
};

export const updateCampaign = async (campaignId, updatedData) => {
  return axiosInstance.put(`/campaigns/update/${campaignId}`, updatedData, { headers: getHeaders() });
};

export const deleteCampaign = async (campaignId) => {
  return axiosInstance.delete(`/campaigns/delete/${campaignId}`, { headers: getHeaders() });
};

export const getCampaign = async (campaignId) => {
  return axiosInstance.get(`/campaigns/${campaignId}`, { headers: getHeaders() });
};

export const getFreshBrandCampaigns = async () => {
  return axiosInstance.get(`/campaigns/brandCampaigns/all`, { headers: getHeaders() });
};


export const startCampaign = async (campaignId) => {
  return axiosInstance.put(`/campaigns/start/${campaignId}`,{placeholder : true}, {headers: getHeaders()})
}

export const endCampaign = async (campaignId) => {
  return axiosInstance.put(`/campaigns/end/${campaignId}`,{placeholder : true}, {headers: getHeaders()})
}


//---------------------------------------------------------------------------------------------------------------------------------------

export const requestToJoinCampaign = async (campaignId) => {
  return axiosInstance.post(`/campaigns/${campaignId}/join-request`, {}, { headers: getHeaders() });
};

// Send a chat message within a campaign


export const sendChatRequest = async (campaignId) => {
  try {
    const response = await axiosInstance.post(`/campaigns/${campaignId}/chat/request`, {}, { headers: getHeaders() });
    return response.data; // Return the response data
  } catch (error) {
    console.error('Error sending chat request:', error);
    throw error; // Propagate error for handling in the component
  }
};


export const updateChatRequestStatus = async (campaignId, influencerId, status) => {
    const response = await axiosInstance.post(`/campaigns/${campaignId}/chat/request/${influencerId}`, {
      status : status,  // 'Accepted' or 'Rejected'
    }, {headers : getHeaders()});
    return response.data;
};


export const sendMessage = async (campaignId, messageData, influencerId) => {
  return axiosInstance.post(
    `/campaigns/${campaignId}/chat/send-message`,
    { ...messageData, influencer_id: influencerId },
    { headers: getHeaders() }
  );
};

// export const sendMessage = (campaignId, messageData, influencerId) => {
//   const messagePayload = {
//     campaign_id: campaignId,
//     content: messageData.content,
//     influencer_id: influencerId,
//     token: localStorage.getItem('access_token')  // attach token here if necessary
//   };
//   socket.emit('send_message', messagePayload);
// };

// export const joinChatRoom = (campaignId, influencerId) => {
//   const joinPayload = {
//     campaign_id: campaignId,
//     influencer_id: influencerId,
//   };
//   console.log('join chat room')
//   socket.emit('join_chat', joinPayload);
// };


// Get all chat messages for a campaign
export const getChatMessages = async (campaignId, influencerId) => {
  return axiosInstance.get(`/campaigns/${campaignId}/chat/messages`, {
    headers: getHeaders(),
    // params: { influencer_id: influencerId } // Pass influencer_id as a query parameter
  });
};



// Respond to a join request (for brands to accept/reject influencer requests)
export const respondToJoinRequest = async (influencerId,campaignId,respondData) => {
  return axiosInstance.put(`/campaigns/join-request/${influencerId}/respond/${campaignId}`, respondData, { headers: getHeaders() });
};


//-----------------------------------------------------------------------------------------------------------------------------------------------------
export const getCampaignTaskData = async (campaignId) => {
  try {
    const response = await axiosInstance.get(`/campaigns/${campaignId}/tasks`, { headers: getHeaders() });
    return response.data;
  } catch (error) {
    console.error('Error fetching campaign task data:', error);
    throw error;
  }
};

export const markTaskAsCompleted = async (taskId, campaignId) => {
  try {
    const response = await axiosInstance.put(`/campaigns/tasks/${taskId}/mark-completed/${campaignId}`, {}, { headers: getHeaders() });
    return response.data;
  } catch (error) {
    console.error('Error marking task as completed:', error);
    throw error;
  }
};

export const approveRejectTask = async (taskId, status, influencerId, feedback, campaignId) => {
  try {
    const response = await axiosInstance.post(`/campaigns/${campaignId}/tasks/${taskId}/approve-reject`, { status, influencerId, feedback }, { headers: getHeaders() });
    return response.data;
  } catch (error) {
    console.error(`Error ${status === 'accepted' ? 'approving' : 'rejecting'} task:`, error);
    throw error;
  }
};

//Notification---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

export const sendCampaignRequestToInfluencer = async (campaign_ID, influencer_ID) => {
  try {
    const response = await axiosInstance.post(`/campaigns/${campaign_ID}/influencers/${influencer_ID}/requests`, {}, {headers : getHeaders()});
    return response.data;
  } catch (error) {
    console.error('Error sending campaign request to influencer:', error);
    throw error;
  }
};



//Metrics and Analytics------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
export const postmediaforinfluencerSocials = async (campaignId, platformLinks) => {
  return axiosInstance.post(`/campaign/tracking/${campaignId}/influencer/post-media`, {'platformLinks' : platformLinks}, { headers: getHeaders() });
};

export const updatepostmetrics = async (campaignId) => {
  return axiosInstance.post(`/campaign/tracking/${campaignId}/updatepostmetrics`, {}, { headers: getHeaders() });
};

export const deletepostmetrics = async (campaignId, link, platform) => {
  return axiosInstance.delete(
    `/campaign/tracking/${campaignId}/influencer/delete-post-tracking`, 
    { 
      headers: getHeaders(),  // Make sure the Authorization header is included here
      data: {                // Send platform and link in the request body as data
        platform: platform,
        link: link
      }
    }
  );
};

export const retrievebrandSocials = async (campaignId) => {
  const response = await axiosInstance.get(`/campaign/tracking/${campaignId}/brandSocials/metric`, { headers: getHeaders() });
  return response.data
};

export const updatepaymentAmount = async (campaignId, influencerId, paymentAmount) => {
  return axiosInstance.put(
    `campaigns/update/payment/${campaignId}/${influencerId}`,
    { payment_amount: paymentAmount },
    { headers: getHeaders() }
  );
}

export const retrieveutmLinks = async (campaignId,influencerId) => {
  return axiosInstance.get(`/campaigns/${campaignId}/generate/links/${influencerId}`, { headers: getHeaders() } )
}

export const retrieveGa4Data = async (campaignId) => {
  return axiosInstance.get(
    `/campaigns/${campaignId}/ga4DataApi`,{ headers: getHeaders() });
}