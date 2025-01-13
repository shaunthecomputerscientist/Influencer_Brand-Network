import { createRouter, createWebHistory } from 'vue-router';
// import Signup from '../components/Signup.vue';
import Login from '../components/auth/Loginn.vue';
import Dashboard from '../views/Dashboard.vue';
import HomeView from '../views/HomeView.vue';
import Signup from '../views/Signup.vue';
import Profile from '../components/user/Profile.vue';
import EditProfile from '../views/EditProfile.vue';
import forgotpassword from '../components/auth/forgotpassword.vue';
import Oauthredirection from '../components/auth/Oauthredirection.vue';
import ResetPassWord from '../views/ResetPassWord.vue';
import Campaign from '../components/campaigns/Campaign.vue';
import CampaignDetail from '../components/campaigns/CAmpaignDetails.vue';
import Subscription from '../views/Subscription.vue';

const routes = [
  { path: '/', component: HomeView },
  { path: '/auth/signup', component: Signup },
  { path: '/auth/login', component: Login },
  { path: '/dashboard', component: Dashboard },
  { path: '/user/profile', component: Profile },
  { path: '/user/user-profile/:id?', component: Profile },
  { path: '/user/profile/edit', component: EditProfile},
  { path: '/auth/forgot-password', component: forgotpassword},
  {
    path: '/auth/google/callback',
    component: Oauthredirection,
  },
  { path: '/reset-password', component: ResetPassWord },
  { path: '/campaigns', component: Campaign},
  {
    path: '/campaign/:id',
    name: 'CampaignDetails',
    component: CampaignDetail,
    props: true, // Pass the route param as a prop
  },
  {path : '/subscription/plans', component: Subscription}
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
