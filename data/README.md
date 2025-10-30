# Datasets

This directory contains datasets that can be used to seed the service. Datasets are loaded into the service using
[IntelliJ HTTP Client CLI](https://www.jetbrains.com/help/idea/http-client-cli.html).

## Prerequisities

1. Ensure that you have [configured the app](../README.md#configure-the-app)
1. [Run the service locally](../README.md#running-locally)
1. Add your GOV.UK One Login email address to the [example users](example.http)

## Loading the example dataset

To load the example dataset into the service:

   ```bash
   cd data
   ./run.sh example.http
   ```
