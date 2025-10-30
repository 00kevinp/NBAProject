
# library necessary packages
library("dplyr")
library(tidymodels)
library(rpart)
library(rpart.plot)
library(doParallel)
library(randomForest)
library(caret)

# get the df from csv file
df <- read.csv("combined_final_dataV2.csv")

# add result column, 1 = win, 0 = loss
df <- df %>%
  group_by(GAME_ID) |>
  mutate(RESULT = case_when(
    PTS == max(PTS) ~ 1,
    TRUE ~ 0
  )) |>
  ungroup() 

df_model <- df %>%
  select(-GAME_ID, -TEAM_ID, -TEAM_ABBREVIATION, -TEAM_CITY, -PTS)


set.seed(123)  
train_index <- createDataPartition(df_model$RESULT, p = 0.8, list = FALSE)

train_data <- df_model[train_index, ]
test_data  <- df_model[-train_index, ]


rfc <- randomForest(RESULT ~ ., data = train_data, ntree = 100)

y_pred <- predict(rfc, newdata = test_data)

mean(y_pred == test_data$RESULT)

table(y_pred == test_data$RESULT)
