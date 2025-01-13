import { createPinia } from 'pinia';
import {useAuthStore} from './modules/auth.js';
import useCampaignsStore from './modules/campaigns.js';
import useInfluencerStore from './modules/influencerStore.js';


// import createPersistedState from 'vuex-persistedstate';

// const store = createStore({
//   modules: {
//     auth
//   }
// });

const pinia = createPinia();


export {pinia, useAuthStore, useCampaignsStore, useInfluencerStore};
// export default pinia;