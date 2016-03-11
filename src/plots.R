library(ggplot2)
library(scales)

all_col <- c("zip","avg_r_d","max_r_d","avg_r_inc","max_r_inc","avg_h1_r_d","max_h1_r_d","avg_h2_r_d","max_h2_r_d","avg_h3_r_d","max_h3_r_d","avg_h4_r_d","max_h4_r_d")
num_col <- c("avg_r_d","max_r_d","avg_r_inc","max_r_inc","avg_h1_r_d","max_h1_r_d","avg_h2_r_d","max_h2_r_d","avg_h3_r_d","max_h3_r_d","avg_h4_r_d","max_h4_r_d")

tmp <- read.csv2("../data/output/model.csv", header = FALSE, sep = "," , stringsAsFactors = FALSE,
                    col.names = all_col)

myData <- as.data.frame(sapply(tmp[num_col], as.numeric))
myData$zip <- tmp$zip
rm(tmp)

ggplot(myData) +
    aes(x=avg_r_d, y=avg_r_inc) +
    geom_point(aes(color = max_h4_r_d)) +
    scale_colour_gradientn(colours=rainbow(4), name = "Mean 4p+\nRenter Density") +
    ggtitle("Mean Renter Income\nby Renter Density") +
    labs(x="Mean Renter Density", y="Mean Renter Income")

ggplot(myData) +
    aes(x=avg_r_d, y=avg_r_inc) +
    geom_point(aes(color = max_h3_r_d)) +
    scale_colour_gradientn(colours=rainbow(4), name = "Mean 3p\nRenter Density") +
    ggtitle("Mean Renter Income\nby Renter Density") +
    labs(x="Mean Renter Density", y="Mean Renter Income")

ggplot(myData) +
    aes(x=avg_r_d, y=avg_r_inc) +
    geom_point(aes(color = max_h2_r_d)) +
    scale_colour_gradientn(colours=rainbow(4), name = "Mean 2p\nRenter Density") +
    ggtitle("Mean Renter Income\nby Renter Density") +
    labs(x="Mean Renter Density", y="Mean Renter Income")

ggplot(myData) +
    aes(x=avg_r_d, y=avg_r_inc) +
    geom_point(aes(color = max_h1_r_d)) +
    scale_colour_gradientn(colours=rainbow(4), name = "Mean 1p\nRenter Density") +
    ggtitle("Mean Renter Income\nby Renter Density") +
    labs(x="Mean Renter Density", y="Mean Renter Income")


aes(x=seq_along(zip), y=avg_r_d) +
    geom_point(aes(color=avg_r_inc, size=max_h4_r_d, title="name")) +
    scale_size(name = "Max Mean\n4+ persons") +
    scale_colour_gradientn(colours=rainbow(4), name = "Mean Renter\nIncome") +
    ggtitle("Mean Renter Features\nfor Nassau County") +
    labs(x="Zipcodes", y="Mean Renter Density") +
    theme(legend.title = element_text(colour="blue", size=10, face="italic"))




ggplot(myData) +
    aes(x=avg_r_d) +
    geom_histogram(binwidth = 0.02,
                   col="red",
                   fill="green",
                   alpha = .2) +
    ggtitle("Mean Renter Density\nfor Nassau County") +
    labs(x="Mean Renter Density", y="Frequency")

ggplot(myData) +
    aes(x=avg_h1_r_d) +
    geom_histogram(binwidth = 0.02,
                   col="red",
                   fill="green",
                   alpha = .2) +
    ggtitle("Mean 1p Renter Density\nfor Nassau County") +
    labs(x="Mean Renter Density", y="Frequency")

ggplot(myData) +
    aes(x=avg_h2_r_d) +
    geom_histogram(binwidth = 0.02,
                   col="red",
                   fill="green",
                   alpha = .2) +
    ggtitle("Mean 2p Renter Density\nfor Nassau County") +
    labs(x="Mean Renter Density", y="Frequency")

ggplot(myData) +
    aes(x=avg_h3_r_d) +
    geom_histogram(binwidth = 0.02,
                   col="red",
                   fill="green",
                   alpha = .2) +
    ggtitle("Mean 3p Renter Density\nfor Nassau County") +
    labs(x="Mean Renter Density", y="Frequency")

ggplot(myData) +
    aes(x=avg_h4_r_d) +
    geom_histogram(binwidth = 0.02,
                   col="red",
                   fill="green",
                   alpha = .2) +
    ggtitle("Mean 4+p Renter Density\nfor Nassau County") +
    labs(x="Mean Renter Density", y="Frequency")


ggplot(myData) +
    aes(x=avg_r_inc) +
    geom_histogram(binwidth = 5000,
                   col="red",
                   fill="green",
                   alpha = .2) +
    ggtitle("Mean Renter Income\nfor Nassau County") +
    labs(x="Mean Renter Income", y="Frequency") +
    scale_x_continuous(labels = comma)


ggplot(myData) +
    aes(x=seq_along(zip), y=avg_r_d) +
    geom_point(aes(color=avg_r_inc, size=max_h4_r_d) +
    scale_size(name = "Max Mean\n4+ persons") +
    scale_colour_gradientn(colours=rainbow(4), name = "Mean Renter\nIncome") +
    ggtitle("Mean Renter Features\nfor Nassau County") +
    labs(x="Zipcodes", y="Mean Renter Density") +
    theme(legend.title = element_text(colour="blue", size=10, face="italic"))

ggplot(myData) +
    aes(x=seq_along(zip), y=avg_r_d) +
    geom_point(aes(color=avg_r_inc, size=max_h3_r_d) +
    scale_size(name = "Max Mean\n3 persons") +
    scale_colour_gradientn(colours=rainbow(4), name = "Mean Renter\nIncome") +
    ggtitle("Mean Renter Features\nfor Nassau County") +
    labs(x="Zipcodes", y="Mean Renter Density") +
    theme(legend.title = element_text(colour="blue", size=10, face="italic"))

ggplot(myData) +
    aes(x=seq_along(zip), y=avg_r_d) +
    geom_point(aes(color=avg_r_inc, size=max_h2_r_d) +
    scale_size(name = "Max Mean\n2 persons") +
    scale_colour_gradientn(colours=rainbow(4), name = "Mean Renter\nIncome") +
    ggtitle("Mean Renter Features\nfor Nassau County") +
    labs(x="Zipcodes", y="Mean Renter Density") +
    theme(legend.title = element_text(colour="blue", size=10, face="italic"))

ggplot(myData) +
    aes(x=seq_along(zip), y=avg_r_d) +
    geom_point(aes(color=avg_r_inc, size=max_h1_r_d) +
    scale_size(name = "Max Mean\n1 person") +
    scale_colour_gradientn(colours=rainbow(4), name = "Mean Renter\nIncome") +
    ggtitle("Mean Renter Features\nfor Nassau County") +
    labs(x="Zipcodes", y="Mean Renter Density") +
    theme(legend.title = element_text(colour="blue", size=10, face="italic"))

