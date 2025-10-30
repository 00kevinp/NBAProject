library("dplyr")
library(tidymodels)
library(rpart)
library(rpart.plot)
library(doParallel)
set.seed(1010)

# pre-processing data
df <- read.csv("covid_stats_cleaned.csv")
df<- df %>%
  group_by(GAME_ID) |>
  mutate(result = case_when(
    PTS == max(PTS) ~ "Win",
    PTS != max(PTS) ~ "Loss"
  ))
  
# basic EDA

# which team won the most games during the COVID seasons?

most_wins <- df %>%
  group_by(TEAM_NAME) |>
  summarise(wins = sum(result == "Win"),
            losses = sum(result == "Loss"),
            games_played = n()) |>
  arrange(desc(wins))

# need to remove row 31, included header (actually introduced me to an error I hadn't noticed prior)
most_wins <- most_wins[-31, ]

ggplot(most_wins, mapping = aes(x = TEAM_NAME, y = wins, colour = TEAM_NAME)) + geom_point() + labs(x = "Teams", y = "Wins", title = "Most Wins During COVID Seasons")

# we can see it's pretty all over the place, which is to be expected. However the 76ers appear to be the most winning team throughout this time period. Despite this data not including playoff games, the Lakers won the championship in 2019, and they have the third highest wins during this period.

# which team had the most 3PM and does that correlate to wins?


df <- df %>%
  mutate(FG3M = as.numeric(FG3M))

most_threes_made <- df %>%
  group_by(TEAM_NAME) |>
  summarise(
    total_FG3M = sum(FG3M),
    wins = sum(result == "Win")) |>
  arrange(desc(total_FG3M), desc(wins))

most_threes_made_highlightLakers <- most_threes_made %>%
  mutate(is_lakers = case_when(
    TEAM_NAME == "Lakers" ~ "Lakers", 
    TEAM_NAME != "Lakers" ~ "Other"
  ))

# doesn't seem to be too strongly correlated but let's look closer using a scatterplot

y_ <- most_threes_made$total_FG3M
x_ <- most_threes_made$wins

ggplot(most_threes_made, mapping = aes(x = x_, y = y_)) + geom_point() + labs(x = "Total Wins", y = "Total Three's Made", title = "Total Three's Made Over Amount of Games Won")

# based on the plot, there is a slight linear correlation, it seems to me the best teams find a happy medium, also the Lakers were an outlier this season

# Let's see the Lakers on the scatterplot now

ggplot(most_threes_made_highlightLakers, mapping = aes(x = x_, y = y_, color = is_lakers)) + geom_point() + labs(x = "Total Wins", y = "Total Three's Made", title = "Total Three's Made Over Amount of Games Won")

# This is really interesting considering the Lakers won the championship in 2019! In a world full of team's shooting three's, the Lakers focused heavily on regular field goals. This is important because later on when we select predictors, this may help ultimately decide if FG3M should be included.

# What else may affect winning? Let's make similar scatterplots using various stats.

df <- df %>% mutate(FTM = as.numeric(FTM))

free_throws_and_wins <- df %>%
  group_by(TEAM_NAME) |>
  summarise(
    total_FTM = sum(FTM),
    wins = sum(result == "Win")) |>
  arrange(desc(total_FTM), desc(wins))
 
 
ggplot(free_throws_and_wins, mapping = aes(x = wins, y = total_FTM)) + geom_point() + labs(x = "Total Wins", y = "Total Free Throw's Made", title = "Total Free Throw's Made Over Amount of Games Won")

# Lastly, lets check how offensive and defensive rebounds play a role in winning

df <- df %>% mutate(OREB = as.numeric(OREB)) |> mutate(DREB = as.numeric(DREB))
offRebound_and_defRebound <- df %>%
  group_by(TEAM_NAME) |>
  summarise(
    total_rebounds = sum(OREB + DREB),
    wins = sum(result == "Win")) |>
  arrange(desc(total_rebounds), desc(wins))

ggplot(offRebound_and_defRebound, mapping = aes(x = wins, y = total_rebounds)) + geom_point() + labs(x = "total wins", y = "total rebounds")

# seems like all of these stats are roughly linearly correlated -- lets use these as features and do some modeling!

# we could use linear regression to predict point outcome, which can be used to predict wins
# or we could use a logistic regression classifier to predict the binary outcome of a win or loss.

# i think using decision tree and logistic regression to predict game outcomes is the best bet


# logistic regression
# following the intro_classification slides

# convert win --> 1, loss --> 0

df <- df %>%
  mutate(result = case_when(
    result == "Win" ~ 1,
    result == "Loss" ~ 0
  ))

glm_fit <- glm(result ~ FG3M + FTM + OREB + DREB, data = df, family = binomial())
summary(glm_fit)

# based on these results, FG3M and FTM are pretty significant, OREB are much less significant than i anticipated, and DREB are highly significant

df <- df %>%
  mutate(FG_PCT = as.numeric(FG_PCT)) |> mutate(FG3_PCT = as.numeric(FG3_PCT)) |> mutate(FT_PCT = as.numeric(FT_PCT))

df <- df %>%
  drop_na(DREB, FG_PCT, FG3_PCT, FT_PCT, result)

glm_fit <- glm(result ~ DREB + FG_PCT + FG3_PCT + FT_PCT, data = df, family = binomial())
summary(glm_fit)
df$prediction_to_win <- predict(glm_fit, type = "response")
df$predicted_result <- ifelse(df$prediction_to_win > 0.5, 1, 0)

mean(df$predicted_result == df$result)

# decision tree
# following the tree_methods.R doc

split <- initial_split(df, prop = 0.8)

training <- training(split)
testing <- testing(split)

cv_samples <- vfold_cv(training)

model <- decision_tree(mode = "regression", 
                       cost_complexity = tune(), 
                       tree_depth = tune()) %>% 
  set_engine("rpart")

# data recipe
data_recipe <- recipe(result ~ DREB + FG_PCT + FG3_PCT + FT_PCT, training)

# workflow
wf_dt <- workflow() %>% 
  add_recipe(data_recipe) %>% 
  add_model(model)

tree_grid <- grid_regular(cost_complexity(),
                          tree_depth(range = c(1, 3)),
                          levels = 3)

tree_res <- wf_dt %>% 
  tune_grid(
    resamples = cv_samples,
    grid = tree_grid,
    control = control_grid(save_pred = TRUE)
  )


# finds the best tree
best_tree <- tree_res %>% 
  select_best(metric = "rmse")


# finalize the workflow
final_wf <- wf_dt %>% 
  finalize_workflow(best_tree)


# predictions of tuned model
preds <- final_wf %>% 
  last_fit(split) %>% 
  collect_predictions()


mean(preds$result)


# comparing the two models

data.frame(
  logistic_regression = mean(df$predicted_result == df$result),
  decision_tree = mean(preds$result)
)