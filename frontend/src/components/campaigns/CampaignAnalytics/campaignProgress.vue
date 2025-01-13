<template>
    <section>
        <div class="d-flex justify-content-between align-items-center my-4">
            <!-- Refresh button can be added here if needed -->
        </div>

        <div v-if="authStore.userProfile.role === 'influencer'" class="hide-scrollbar d-flex gap-3" style="overflow: auto;">
            <p class="btn btn-info alert alert-secondary">Total Tasks: <span>{{ campaign.tasks.length }}</span></p>
            <p class="btn btn-info alert alert-secondary">Completed Tasks: <span>{{ completedTasksCount }}</span></p>
            <p class="btn btn-info alert alert-secondary">Pending Tasks: <span>{{ campaign.tasks.length-completedTasksCount }}</span></p>
        </div>

        <!-- Influencer-Specific View -->
        <div v-if="authStore.userProfile.role === 'influencer'" class="influencer-view mt-4">
            <!-- <h3 class="text-secondary fw-bold" style="text-decoration: underline;">Your Tasks</h3> -->
            <!-- <p>{{ influcencerTasks }}</p> -->
            <div v-for="task in influcencerTasks" class="task-card alert alert-warning p-3 my-2">
                <div class="d-flex justify-content-around p-2 w-100">
                   <div class="d-flex gap-2 flex-wrap justify-content-around tooltipp">
                        <button class="">Task {{ parseInt(task.task_id) }}</button>
                        <div class="tooltiptext">
                            <p>{{ task.task_description }}</p>
                        </div>
                    </div>
                    <span :class="[task.status, 'd-flex text-wrap align-items-center justify-content-center alert alert-info']"> Status: {{ task.status==='null'?'None':task.status }}</span>
                    <span v-if="task.status==null || task.status === 'null' || task.status === 'rejected'" :disabled="task.status==='accepted' || disableButton" @click="markAsCompleted(task.task_id)" class="btn btn-success d-flex align-items-center justify-content-center mt-2" style="height: 2rem;">
                        <i class="fa fa-check" style="font-size: small;"></i>
                    </span>
                </div>
            </div>
            <div class="progress">

                            <div
                                class="progress-bar progress-bar-striped bg-info progress-bar-animated"
                                role="progressbar"
                                :style="{ width: (filteredInfluencer.taskProgress * 100) + '%' }"
                                aria-valuenow="filteredInfluencer.taskProgress * 100"
                                aria-valuemin="0"
                                aria-valuemax="100">
                {{ Math.round(filteredInfluencer.taskProgress * 100) }}% completed
            </div>
            </div>
        </div>

        <!-- Sponsor View - Overview of All Influencer Progress -->
        <div v-if="authStore.userProfile.role === 'brand'" class="sponsor-view mt-4">
            <!-- <h3 class="text-secondary fw-bold" style="text-decoration:underline">Track Task Completions</h3> -->
            <div v-if="pendingTasksStatus.length!==0" v-for="influencer in pendingTasksStatus" class="influencer-progress p-3 w-100">
                <button class="w-100" :key = "influencer.influencer_id" @click="toggleshowInfluencer(influencer.influencer_id)" >{{ influencer.influencer_name }}</button>
                <h6 class="text-warning fw-bold alert alert-warning"> This influencer wants your approval on tasks. Are you satisfied enough to approve?</h6>
                <div v-if="showInfluencerTask[influencer.influencer_id]" v-for="task in influencer.pendingTasks" :key="task.task_id" class="task-card p-3 my-2 border w-100">
                    <div v-if="task.status === 'pending'">
                        <div class="d-flex gap-2 flex-wrap justify-content-around border p-2 w-100">
                                                <div class="d-flex gap-2 flex-wrap justify-content-around tooltipp">
                                                <button>Task {{ parseInt(task.task_id) + 1 }}</button>
                                                <div class="tooltiptext">
                                                    <p>{{ task.task_description }}</p>
                                                </div>
                                            </div>
                            
                            <div>
                                <input 
                                type="text" 
                                v-model="feedbacks[generateFeedbackKey(influencer.influencer_id, task.task_id)]" 
                                placeholder="Enter feedback" 
                                class="form-control"/> 
                            </div>

                            <div class="d-flex gap-2">
                                <button v-if="task.status === 'pending' || task.status === 'rejected'" @click="approveTask(task.task_id, influencer.influencer_id)" class="btn btn-success"><i class="fa fa-check"></i></button>
                                <button v-if="task.status === 'pending' || task.status === 'accepted'" @click="rejectTask(task.task_id, influencer.influencer_id)" class="btn btn-danger"><i class="fa fa-x"></i></button>
                            </div>
                        </div>
                    </div>
                    
                    <div v-else class="d-flex">
                        <div class="tooltipp d-flex align-items-center justify-content-center">
                            <button>Task {{ parseInt(task.task_id) + 1 }}</button>
                            <div class="tooltiptext">
                                <p>{{ task.status === null ? 'Not Completed' : '' }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else class="alert alert-warning">
                <h6>No requests for task approval.</h6>
            </div>
        </div>
    </section>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useCampaignsStore } from '../../../store';
import { useAuthStore } from '../../../store';

export default {
    name: 'CampaignTaskProgress',
    props: {
        campaign: {
            type: Object,
            required: true,
        },
    },
    setup(props) {
        const campaignsStore = useCampaignsStore();
        const authStore = useAuthStore();
        const tasks = ref([]);
        const feedbacks = ref({}); // Track feedback for each task
        const showInfluencerTask = ref({});
        const disableButton = ref(false);
        const filteredInfluencer = computed(() => {
        // Find the influencer by matching influencer_id
        const influencer = props.campaign.influencers.find(
            (influencer) => influencer.influencer_id === authStore.userProfile.id
        );// to get influencer campaign data of the current  user who is influencer
        
        // If no influencer is found, return a default object with { status: null }
        return influencer || { status: null };
        });


        const generateFeedbackKey = (influencerId, taskId) => {
            return `${influencerId}-${taskId}`;
            };


        const completedTasksCount = computed(() =>
            tasks.value
                .flatMap(influencer => influencer.tasks) // Combine tasks arrays from all influencers
                .filter(task => task.status === 'accepted').length
            );


        const pendingTasksCount = computed(() =>
            tasks.value
                .flatMap(influencer => influencer.tasks) // Combine tasks arrays from all influencers
                .filter(task => task.status === 'pending').length
            );

            const getInfluencerTasks = (influencerId) => computed(() => {
            const influencer = tasks.value.find(i => i.influencer_id === influencerId);
            return influencer ? influencer.tasks : [];
            });

        const influcencerTasks = computed(() => getInfluencerTasks(authStore.userProfile.id).value);
        const toggleshowInfluencer = (influencerId) => {
            showInfluencerTask.value[influencerId] = !showInfluencerTask.value[influencerId];
        };



        const pendingTasksStatus = computed(() => {
            return tasks.value.map(influencer => ({
                ...influencer,
                pendingTasks: influencer.tasks.filter(task => task.status === 'pending')
            })).filter(influencer => influencer.pendingTasks.length > 0);
        });
        console.log(pendingTasksStatus)



        const fetchTasks = async () => {
            try {
                await campaignsStore.loadCampaignTasks(props.campaign.id);
                tasks.value = campaignsStore.campaignTasks;
            } catch (error) {
                console.error("Error fetching tasks:", error);
            }
        };

        const markAsCompleted = async (taskId) => {
            try {
                disableButton.value=true;
                await campaignsStore.markTaskAsCompleted(taskId, props.campaign.id);
                await fetchTasks();
            } catch (error) {
                console.error("Error marking task as completed:", error);
            }
        };

        const approveTask = async (taskId, influencerId) => {
            const feedback = feedbacks.value[`${influencerId}-${taskId}`];
            
            try {
                await campaignsStore.approveRejectTask(taskId, 'accepted', influencerId, feedback, props.campaign.id);
                await fetchTasks();
                feedbacks.value[`${influencerId}-${taskId}`]=''
            } catch (error) {
                console.error("Error approving task:", error);
            }
        };

        const rejectTask = async (taskId, influencerId) => {
            const feedback = feedbacks.value[`${influencerId}-${taskId}`];
            try {
                console.log(props.campaign.id)
                await campaignsStore.approveRejectTask(taskId, 'rejected', influencerId, feedback,props.campaign.id);
                await fetchTasks();
                feedbacks.value[`${influencerId}-${taskId}`]=''
            } catch (error) {
                console.error("Error rejecting task:", error);
            }
        };

        onMounted(fetchTasks);

        return {
            authStore,
            tasks,
            completedTasksCount,
            pendingTasksCount,
            markAsCompleted,
            approveTask,
            rejectTask,
            refreshTasks: fetchTasks,
            feedbacks,
            pendingTasksStatus,
            toggleshowInfluencer,
            showInfluencerTask,
            getInfluencerTasks,
            influcencerTasks,
            disableButton,
            generateFeedbackKey,
            filteredInfluencer
        };
    },
};
</script>

  
  <style scoped>
  .hide-scrollbar::-webkit-scrollbar {
    display: none;
  }
  .hide-scrollbar p{
    padding: 1rem;
    text-wrap: nowrap;
  }
  .hide-scrollbar p:hover {
    background-color: #12dbe6;
    box-shadow: 2px 1px 0.2rem rgb(55, 55, 55);
  }
  .pending {
    background-color: #8b8b8b68;
    padding: 0.5rem;
    border-radius: 0.5rem;
    font-weight: bold;
    font-size: small;
  }
  .accepted {
    background-color: #00922c5d;
    font-weight: bold;
    font-size: small;
    padding: 1rem;
    border-radius: 0.5rem;
  }
  .rejected {
    background-color: #ee090968;
    padding: 0.5rem;
    font-weight: bold;
    font-size: small;
    border-radius: 0.5rem;
  }
  .tooltiptext {
    margin-left: 5rem;
    width: 12rem;
    background-color: rgb(255, 234, 180);
    font-weight: bolder;
    color: orange;
    text-wrap: wrap;
  }


button{
    font-size: small;
    height: 0.5rem;
    width: 3rem;
    height: 3rem;
    padding: 0;
}
button:hover{
    padding: auto;
}
.null{
    font-weight: bold;
    font-size: small;
}
  </style>
  