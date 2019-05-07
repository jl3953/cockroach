#!/usr/bin/env Rscript

library(R.utils)
library(scales)
library(magrittr)
library(dplyr)
library(readr)
library(tidyr)
library(ggplot2)

csv <- cmdArg("csv")
out <- cmdArg("out")

if (is.null(csv)) {
  throw("--csv argument required")
}

if (is.null(out)) {
  throw("--out argument required")
}

measurements <- read_csv(csv)

data <- measurements %>%
  filter(sample_type %in% c("total_aggregate")) %>%
  select(
    "p50_ms",
    "p95_ms",
    "p99_ms",
    "key_dist_skew"
  ) %>%
  rename(
    "skew" = "key_dist_skew"
  )

data %>%
  ggplot(aes(x = skew)) +
  geom_point(aes(y = p50_ms, color = "50th"), stat = "identity") +
  geom_line(aes(y = p50_ms, color = "50th"), stat = "identity") +
  geom_point(aes(y = p95_ms, color = "95th"), stat = "identity") +
  geom_line(aes(y = p95_ms, color = "95th"), stat = "identity") +
  geom_point(aes(y = p99_ms, color = "99th"), stat = "identity") +
  geom_line(aes(y = p99_ms, color = "99th"), stat = "identity") +
  labs(
    x = "Zipf Skew",
    y = "Latency (ms)",
    color = "Percentile"
  ) +
  scale_x_continuous(labels = number_format(accuracy = 0.01)) +
  scale_y_continuous(labels = comma) +
  theme_classic()

ggsave(out)