import numpy as np
import pandas as pd


def prepare_age_dist():
    workers_by_age = pd.read_csv('workers.csv', index_col='Age_Group')

    total_males = workers_by_age.loc['Total']['Total_Males']
    male_working_pop_total = workers_by_age.loc['Total']['Main_Working_Males']
    male_non_working_pop_total = total_males - male_working_pop_total

    total_females = workers_by_age.loc['Total']['Total_Females']
    female_working_pop_total = workers_by_age.loc['Total']['Main_Working_Females']
    female_non_working_pop_total = total_females - female_working_pop_total

    workers_by_age["Male_Working_Probability"] = workers_by_age["Main_Working_Males"] / male_working_pop_total
    workers_by_age["Female_Working_Probability"] = workers_by_age["Main_Working_Females"] / female_working_pop_total
    workers_by_age["Male_Non_Working_Probability"] = (workers_by_age['Total_Males'] - workers_by_age[
        'Main_Working_Males']) / male_non_working_pop_total
    workers_by_age["Female_Non_Working_Probability"] = (workers_by_age['Total_Females'] - workers_by_age[
        'Main_Working_Females']) / female_non_working_pop_total

    workers_by_age = workers_by_age.drop('Total')

    print(workers_by_age)
    return workers_by_age


def generate_population():
    df = pd.read_csv('ward_wise_dataset.csv')

    # Validate if all Males + Females = Total Population
    assert (df["Total_Males"] + df["Total_Females"]).equals(df["Total_Pop"])

    age_dist = prepare_age_dist()

    # making an assumption and applying it all working population
    public_transport_probability = 0.2

    population = {}
    counter = 0

    for index in df.index:
        ward = df['Ward'][index]
        n_males_in_ward = df["Total_Males"][index]
        n_females_in_ward = df["Total_Females"][index]

        n_working_males_in_ward = df['Main_Working_Males'][index]
        n_non_working_males_in_ward = n_males_in_ward - n_working_males_in_ward
        n_working_females_in_ward = df['Main_Working_Females'][index]
        n_non_working_females_in_ward = n_females_in_ward - n_working_females_in_ward

        for i in range(n_working_males_in_ward):
            age = calc_age("Male_Working_Probability", age_dist)
            pub_transport = choose_pub_transport(True, public_transport_probability)
            population[counter] = {'ind': counter, 'ward': ward, 'sex': 'M', 'age': age, 'working': True,
                                   'pub_transport': pub_transport}
            counter += 1

        for i in range(n_non_working_males_in_ward):
            age = calc_age("Male_Non_Working_Probability", age_dist)
            pub_transport = choose_pub_transport(False, public_transport_probability)
            population[counter] = {'ind': counter, 'ward': ward, 'sex': 'M', 'age': age, 'working': False,
                                   'pub_transport': pub_transport}
            counter += 1

        for i in range(n_working_females_in_ward):
            age = calc_age("Female_Working_Probability", age_dist)
            pub_transport = choose_pub_transport(True, public_transport_probability)
            population[counter] = {'ind': counter, 'ward': ward, 'sex': 'F', 'age': age, 'working': True,
                                   'pub_transport': pub_transport}
            counter += 1

        for i in range(n_non_working_females_in_ward):
            age = calc_age("Female_Non_Working_Probability", age_dist)
            pub_transport = choose_pub_transport(False, public_transport_probability)
            population[counter] = {'ind': counter, 'ward': ward, 'sex': 'F', 'age': age, 'working': False,
                                   'pub_transport': pub_transport}
            counter += 1

    population_df = pd.DataFrame.from_dict(population, 'index',
                                           columns=['ward', 'sex', 'age', 'working', 'pub_transport'])
    population_df.to_csv("output.csv", index_label='ind')


def calc_age(col, age_dist):
    working_age_groups = ["20-24", "25-29", "30-34", "35-39", "40-49", "50-59"]
    df_age_groups = ["00-04", "05-09", "10-14", "15-19", ] + working_age_groups + ["60-69", "70-79", "80+", "Age not stated"]
    choice = np.random.choice(a=df_age_groups, p=age_dist[col].tolist())
    if choice == "Age not stated":  # hack: assume any age uniformly between 20-59
        return np.random.choice(a=working_age_groups)
    return choice


def choose_pub_transport(working, public_transport_probability):
    if working:
        return np.random.choice(a=[True, False], p=[public_transport_probability, 1 - public_transport_probability])
    return False


if __name__ == "__main__":
    generate_population()
