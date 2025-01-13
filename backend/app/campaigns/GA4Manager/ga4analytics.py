from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest, OrderBy
from datetime import date, datetime
import uuid
import json
import pandas as pd
import os
from models.models import Campaign, SocialLink

class GA4CampaignManager:
    def __init__(self, campaign, ga4_property_id, service_account_info):
        """
        Initialize the GA4CampaignManager class.

        :param campaign: A Campaign object from your app models, containing campaign data (e.g., start_date, end_date, name, etc.)
        :param ga4_property_id: The GA4 Property ID.
        :param service_account_info: Service account info as JSON, used for GA4 API authentication.
        """
        self.campaign = campaign
        self.ga4_property_id = ga4_property_id
        if isinstance(service_account_info, str):
            service_account_info = json.loads(service_account_info)  # Convert from JSON string to Python dict        
        self.client = BetaAnalyticsDataClient.from_service_account_info(service_account_info)
        with open(os.path.join(os.getcwd(),'campaigns','GA4Manager','utm_mapping.json'), 'r') as file:
            self.utm_mapping = json.load(file)
            # remember to make utm platforms lower case later
        self.utm_parameters = {
              'utm_campaign': self.campaign.name.replace(' ','').strip()  # Ensure to use campaign name or ID
          }

    def generate_utm_links(self, base_urls, platforms, influencer_id=None, include_affiliate=False):

        tracking_links = []
        # print(platforms, influencer_id)
        if not isinstance(base_urls, list):
            base_urls = [base_urls]

        platforms = [x.lower() for x in platforms]
        # print(platforms)
        # print(self.utm_mapping['utm_mapping'][([platforms[0]][0].lower())])
          # Loop over base URLs and platforms to generate UTM links
        for base_url in base_urls:
            if '/'!=base_url[-1]:
              base_url=base_url+'/'
            for platform in platforms:
                if platform in self.utm_mapping['utm_mapping'].keys():
                    # Get the corresponding source and medium for the platform
                    # print('platforms')
                    self.utm_parameters['utm_source'] = self.utm_mapping['utm_mapping'][platform]['source']
                    self.utm_parameters['utm_medium'] = self.utm_mapping['utm_mapping'][platform]['medium']
                    self.utm_parameters['utm_content'] = platform # Track platform in utm_content
                    # print(self.utm_parameters)

                    # Add influencer ID in utm_term even if include_affiliate is False
                    if influencer_id:
                        self.utm_parameters['utm_term'] = str(influencer_id)  # Track influencer with utm_term

                    # If affiliate tracking is enabled, modify the medium
                    if include_affiliate:
                        self.utm_parameters['utm_medium'] += '_affiliate'  # Modify medium to indicate affiliate

                    # Generate the tracking link
                    query_params = '&'.join([f"{k}={v}" for k, v in self.utm_parameters.items()])
                    tracking_link = f"{base_url}?{query_params}"
                    # print(tracking_link)

                    # Create a JSON object for this link
                    tracking_links.append({
                        'influencer_id': influencer_id if influencer_id else None,
                        'platform': platform,
                        'utm_link': tracking_link,
                        'created_at': datetime.utcnow().isoformat()  # Store the current timestamp
                    })
        # Return the JSON object corresponding to the influencer ID
        return tracking_links if len(tracking_links)>0 else None  # Return None if no links are generated

    def format_report(self,request):
            response = self.client.run_report(request)

            # Get the dimension names
            row_index_names = [header.name for header in response.dimension_headers]

            # Collect dimension values for each row
            row_data = []
            for row in response.rows:
                row_data.append([dimension_value.value for dimension_value in row.dimension_values])

            # Collect metric names and their corresponding values
            metric_names = [header.name for header in response.metric_headers]
            data_values = []
            for row in response.rows:
                data_values.append([float(metric_value.value) for metric_value in row.metric_values])

            # Combine dimension and metric values into a flat DataFrame
            flat_data = pd.DataFrame(data=row_data, columns=row_index_names)
            metrics_df = pd.DataFrame(data=data_values, columns=metric_names)

            # Concatenate dimensions and metrics into a single DataFrame
            output_df = pd.concat([flat_data, metrics_df], axis=1)

            # Convert the 'date' column to datetime and extract the day number
            output_df['date'] = pd.to_datetime(output_df['date'], format='%Y%m%d')  # Ensure date is parsed
            output_df['day'] = output_df['date'].dt.day  # Extract the day number

            # Drop the original 'date' column if you don't need it
            output_df.drop('date', axis=1, inplace=True)

            return output_df

    def fetch_ga4_data(self, campaign, **kwargs):
        """
        Fetch GA4 data without filtering, allowing retrieval of all data related to UTM links.

        Parameters:
        - campaign: Campaign object to use for start and end date.
        - kwargs: Additional filters (optional).

        Returns:
        - DataFrame containing all fetched GA4 data without filtering by specific values.
        """
        # Define default dimensions (including UTM parameters)
        # 'pagePath'
        dimensions = ['month', 'date', 'dayOfWeekName', 'sessionManualMedium', 'sessionCampaignName', 'sessionManualSource', 'sessionManualTerm', 'sessionManualAdContent']
        metrics = ['averageSessionDuration', 'activeUsers', 'bounceRate', 'Sessions', 'totalUsers', 'engagementRate']

        # if datetime.utcnow() < campaign.end_date:
        #    end_date_str = datetime.utcnow().strftime('%Y-%m-%d')
        # else:
        end_date_str = campaign.end_date.strftime('%Y-%m-%d')

        # Convert the campaign start and end dates to string format
        start_date_str = datetime(2024, 10, 20).strftime('%Y-%m-%d')
        # start_date_str = campaign.start_date.strftime('%Y-%m-%d')

        # Create GA4 API request using Dimension, Metric, and DateRange objects
        try:
            request = RunReportRequest(
                property=f"properties/{self.ga4_property_id}",
                dimensions=[Dimension(name=dim) for dim in dimensions],
                metrics=[Metric(name=met) for met in metrics],
                order_bys = [OrderBy(dimension = {'dimension_name': 'month'}),
                    OrderBy(dimension = {'dimension_name': 'date'}), OrderBy(metric = {'metric_name' : 'totalUsers'})],
                date_ranges=[DateRange(start_date=start_date_str, end_date=end_date_str)],
            )

            dataframe = self.format_report(request)
            df = dataframe[dataframe['sessionCampaignName']==campaign.name.lower().replace(' ', '').strip()]
            return df

        except Exception as e:
            print(f"Error fetching GA4 data: {e}")
            return None



def get_platforms_list(influencer_id):
    # Query to filter SocialLink rows by user_id
    social_links = SocialLink.query.filter_by(user_id=influencer_id).all()
    
    # Extract the platform names into a list
    platforms_list = [social_link.platform for social_link in social_links]
    
    return platforms_list

def generate_utm_links_wrapper(campaignId, influencerId, include_affiliate = True):
    campaign = Campaign.query.filter_by(id=campaignId).first()
    manager = GA4CampaignManager(campaign, campaign.ga4_property_id, campaign.ga4_credentials_json)
    platforms_list = get_platforms_list(influencerId)
    tracking_links = manager.generate_utm_links([campaign.ga4_base_url],platforms = platforms_list ,influencer_id=influencerId,include_affiliate=include_affiliate)
    return tracking_links

def get_ga4_Report(campaignId):
    campaign = Campaign.query.filter_by(id=campaignId).first()
    manager = GA4CampaignManager(campaign, campaign.ga4_property_id, campaign.ga4_credentials_json)
    return manager.fetch_ga4_data(campaign)

def aggregate_data(df, influencer_ids):
    # Filter data for influencers
    influencer_ids_str = list(map(lambda x: str(x), influencer_ids))
    influencer_data = df[df["sessionManualTerm"].isin(influencer_ids_str)]
    # Get external data by subtracting influencer IDs from unique session terms
    unique_terms = df["sessionManualTerm"].unique()
    external_ids = [term for term in unique_terms if term not in influencer_ids_str]
    external_data = df[df["sessionManualTerm"].isin(external_ids)]

    print(influencer_ids,external_ids, unique_terms)
    # Aggregated data for influencers
    aggregated_influencer_data = influencer_data.groupby("sessionManualTerm").agg(
        total_sessions=("Sessions", "sum"),
        avg_bounce_rate=("bounceRate", "mean"),
        avg_engagement_rate=("engagementRate", "mean"),
        total_active_users=("activeUsers", "sum"),
    ).reset_index()
    
    # Aggregated data for external users
    aggregated_external_data = external_data.groupby("sessionManualTerm").agg(
        total_sessions=("Sessions", "sum"),
        avg_bounce_rate=("bounceRate", "mean"),
        avg_engagement_rate=("engagementRate", "mean"),
        total_active_users=("activeUsers", "sum"),
    ).reset_index()

    # print('influencer data-------------------------------')
    # print(influencer_data)
    # print('\n')

    # print('external data-------------------------------------------------')
    # print(external_data)
    # print('\n')
    
    # Return four dataframes: aggregated and raw data for both influencers and external users
    return (aggregated_influencer_data,influencer_data, aggregated_external_data, external_data)