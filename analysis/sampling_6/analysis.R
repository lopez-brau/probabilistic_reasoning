# Load libraries.
library(tidyverse)

# Set the working directory.
setwd("D:/Research/probabilistic_reasoning/")

# Read in the human data.
human_0 = read_csv("data/sampling_6/sampling_6.csv") %>%
  left_join(select(read_csv("data/sampling_6/demographics.csv"), -Comments)) 

# Exclude a participant for data entry error.
human_1 = human_0 %>%
  filter(UniqueId!="082218_Uvasichi_443")

# Visualize the raw human data.
human_1 %>%
  ggplot(aes(x=Response, group=Version, fill=Version)) + 
  geom_histogram(stat="count", position="dodge") + 
  facet_wrap(Condition~Trial, scales="free_x", nrow=2) + 
  theme_bw() +
  theme(axis.text.x=element_text(angle=45, hjust=1))

# Strip the color information from the response column.
convert_response = function(response) {
  new_response = c()
  for (i in 1:nchar(response)) {
    if (!is.na(as.numeric(substr(response, i, i)))) {
      new_response = paste(new_response, substr(response, i, i), sep="")
    }
    else {
      new_response = paste(new_response, "_", sep="")
    }
  }
  return(new_response)
}  
human_2 = human_1 %>%
  mutate(Response=sapply(Response, convert_response))

# Visualize the human data after collapsing color conditions.
human_2 %>%
  ggplot(aes(x=Response, group=Version, fill=Version)) + 
  geom_histogram(stat="count", position="dodge") + 
  facet_wrap(~Trial, scales="free_x", nrow=3) + 
  theme_bw() +
  theme(axis.text.x=element_text(angle=45, hjust=1))

# Compute and visualize the percentage endorsements.
human_3 = human_2 %>%
  do(left_join(., summarize(group_by(., Version, Trial), 
                            Trial_Total=n()))) %>%
  group_by(Version, Trial, Response, Trial_Total) %>%
  summarize(Response_Total=n()) %>%
  mutate(Endorsement_Perc=Response_Total/Trial_Total) 

human_3 %>% 
  ggplot(aes(x=Response, y=Endorsement_Perc, group=Version, fill=Version)) + 
  geom_histogram(stat="identity", position="dodge") +
  geom_hline(aes(yintercept=0.5), linetype="dashed", color="black", size=0.5) +
  facet_wrap(~Trial, scales="free_x", nrow=3) +
  theme_bw() +
  theme(axis.text.x=element_text(angle=45, hjust=1)) +
  ylim(0, 1)

# Compute the odds ratio for each option within a trial.
# - For odds ratio > 1: compute a/b and the percentage of participants that
#   chose a
# - For odds ratio < 1: compute -a/b and the percentage of participants that
#   chose b
human_4 = human_3 %>%
  mutate(Endorsement_Ratio=ifelse(Response_Total/(Trial_Total-Response_Total) < 1,
                                  -(Trial_Total-Response_Total)/Response_Total,
                                  Response_Total/(Trial_Total-Response_Total)))

# Read in the model predictions and stitch them to the human data.
data_0 = human_4 %>%
  left_join(read_csv("data/model/model.csv"))

# Find the response with the highest participant endorsement per trial to 
# compare its likelihood ratio with the likelihood ratios predicted by the
# model.
# data_1 = data_0 %>% 
#   ungroup() %>%
#   group_by(Version, Trial) %>% 
#   filter(Response_Total==max(Response_Total)) %>%
#   arrange(Trial)

# Scale the likelihood ratios for both the participant data and the model
# predictions.
data_2 = data_0 %>%
  filter(Version=="EC") %>%
  mutate(z_PMF_Prediction=(PMF_Prediction-mean(.$PMF_Prediction))/sd(.$PMF_Prediction),
         z_DU_Prediction=(DU_Prediction-mean(.$DU_Prediction))/sd(.$DU_Prediction),
         z_BT_Prediction=(BT_Prediction-mean(.$BT_Prediction))/sd(.$BT_Prediction))
data_3 = data_0 %>%
  filter(Version=="P") %>%
  mutate(z_PMF_Prediction=(PMF_Prediction-mean(.$PMF_Prediction))/sd(.$PMF_Prediction),
         z_DU_Prediction=(DU_Prediction-mean(.$DU_Prediction))/sd(.$DU_Prediction),
         z_BT_Prediction=(BT_Prediction-mean(.$BT_Prediction))/sd(.$BT_Prediction))
data_4 = rbind(data_2, data_3) %>%
  gather(Model_Type, Prediction, z_PMF_Prediction, z_DU_Prediction, z_BT_Prediction)

# Visualize the scaled likelihood ratios of the participant data and the model
# predictions.
data_4 %>%
  ggplot(aes(x=Prediction, y=Endorsement_Ratio, label=Trial)) +
  geom_text() +
  geom_abline() + 
  facet_wrap(Version~Model_Type) + 
  theme_bw()
