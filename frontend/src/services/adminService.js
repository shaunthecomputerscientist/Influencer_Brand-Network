import { axiosInstance, getHeaders } from './axiosInstance';

// Function to increase flag count for a campaign
export const increaseCampaignFlag = async (campaignId, feedback) => {
  return axiosInstance.post(
    `/admin/campaigns/${campaignId}/flags`,
    { feedback }, // Pass feedback in the payload
    { headers: getHeaders() }
  );
};

// Function to decrease flag count for a campaign
export const decreaseCampaignFlag = async (campaignId) => {
  return axiosInstance.delete(
    `/admin/campaigns/${campaignId}/flags`,
    { headers: getHeaders() }
  );
};

// Function to retrieve all flagged campaigns (if implemented in the backend)
export const getFlaggedCampaigns = async () => {
  return axiosInstance.get(
    `/admin/campaigns/flags`,
    { headers: getHeaders() }
  );
};


export const increaseInfluencerFlag = async (influencerId, feedback) => {
    return axiosInstance.post(
      `/admin/influencers/${influencerId}/flags`,
      { feedback }, // Pass feedback in the payload
      { headers: getHeaders() }
    );
  };
  
  // Function to decrease flag count for an influencer
export const decreaseInfluencerFlag = async (influencerId) => {
return axiosInstance.delete(
    `/admin/influencers/${influencerId}/flags`,
    { headers: getHeaders() }
);
};
  
  // Function to retrieve all flagged influencers (if implemented in the backend)
export const getFlaggedInfluencers = async () => {
return axiosInstance.get(
    `/admin/influencers/flags`,
    { headers: getHeaders() }
);
};
  
