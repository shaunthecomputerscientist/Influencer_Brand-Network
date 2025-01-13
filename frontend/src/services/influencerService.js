// import axios from 'axios';
import {axiosInstance, getHeaders} from './axiosInstance';

export const fetchInfluencers = async (filters) => {
    return axiosInstance.post(`/user/influencers/search`, filters, { headers: getHeaders() });
  };

  export const fetchInitialInfluencers = async () => {
    return axiosInstance.get(`/user/influencers`, { headers: getHeaders() });
  };
  