import {axiosInstance, getHeaders} from './axiosInstance';


  export const triggerga4export = async (campaignId) => {
    return axiosInstance.post(`triggerjobs/ga4/export`,{'campaign_id':campaignId} ,{ headers: getHeaders() });
  };
  
  export const retrieveGA4Report = async (taskId) => {
    return axiosInstance.get(`triggerjobs/ga4/export/${taskId}`, { headers: getHeaders() });
  }