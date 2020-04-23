import numpy as np
import pandas as pd


def generate_population():
    df = pd.read_csv('ward_wise_dataset.csv')

    # Validate if all Males + Females = Total Population
    assert (df["Tot_Male"] + df["Tot_Female"]).equals(df["Total_Pop"])

    age_df = pd.read_csv('age_dist_by_sex.csv', index_col='Age_Group')
    # The two dataset totals should be in sync
    assert age_df.loc['All ages']['Total'] == df["Total_Pop"].sum()

    total_males_with_age_available = age_df.loc['All ages']['Total_Males'] - age_df.loc['Age not stated']['Total_Males']
    total_females_with_age_available = age_df.loc['All ages']['Total_Females'] - age_df.loc['Age not stated'][
        'Total_Females']
    # Don't consider the 'Age not stated' column for calculating age probability
    male_age_probability = age_df['Total_Males'] / total_males_with_age_available
    female_age_probability = age_df['Total_Females'] / total_females_with_age_available

    # Drop cols we don't need
    male_age_probability = male_age_probability.drop('All ages').drop('Age not stated')
    female_age_probability = female_age_probability.drop('All ages').drop('Age not stated')

    print(male_age_probability)
    print(female_age_probability)

    df_workers = pd.read_csv('workers.csv', index_col='Age_Group')
    df_workers = df_workers[
        ['Total_Pop', 'Total_Males', 'Total_Females', 'Main_Workers_Total', 'Main_Workers_Males',
         'Main_Workers_Females']]  # Consider marginal workers as non-working for now
    print(df_workers)
    assert df_workers.loc['Total', 'Total_Pop'] == df["Total_Pop"].sum()
    assert df_workers.loc['Total', 'Total_Males'] == df["Tot_Male"].sum()
    assert df_workers.loc['Total', 'Total_Females'] == df["Tot_Female"].sum()

    male_working_probability = df_workers['Main_Workers_Males'] / df_workers['Total_Males']
    female_working_probability = df_workers['Main_Workers_Females'] / df_workers['Total_Females']
    male_working_probability = male_working_probability.drop('Total').drop('Age not stated')
    female_working_probability = female_working_probability.drop('Total').drop('Age not stated')

    print(male_working_probability)
    print(female_working_probability)

    # making an assumption and applying it all working population
    public_transport_probability = 0.2

    population = {}
    counter = 0

    for index in df.index:
        ward = df['Ward_name'][index]
        n_males_in_ward = df["Tot_Male"][index]
        n_females_in_ward = df["Tot_Female"][index]
        age_groups = ["00-04", "05-09", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54",
                      "55-59", "60-64", "65-69", "70-74", "75-79", "80+"]

        male_age_samples = np.random.choice(a=age_groups, size=n_males_in_ward, p=male_age_probability)
        for a in male_age_samples:
            working = is_working(male_working_probability, a)
            pub_transport = choose_pub_transport(working, public_transport_probability)
            population[counter] = {'ind': counter, 'ward': ward, 'sex': 'M', 'age': a, 'working': working,
                                   'pub_transport': pub_transport}
            counter += 1

        female_age_samples = np.random.choice(a=age_groups, size=n_females_in_ward, p=female_age_probability)
        for a in female_age_samples:
            working = is_working(female_working_probability, a)
            pub_transport = choose_pub_transport(working, public_transport_probability)
            population[counter] = {'ind': counter, 'ward': ward, 'sex': 'F', 'age': a, 'working': working,
                                   'pub_transport': pub_transport}
            counter += 1

    population_df = pd.DataFrame.from_dict(population, 'index',
                                           columns=['ward', 'sex', 'age', 'working', 'pub_transport'])
    population_df.to_csv("output.csv", index_label='ind')


def is_working(working_probabilities, age):
    def prob_for_age(age_group):
        return [working_probabilities[age_group], 1 - working_probabilities[age_group]]

    def working_status_choice(age):
        return np.random.choice(a=[True, False], p=prob_for_age(age))

    age_to_work = {
        "00-04": lambda: False,
        "05-09": lambda: working_status_choice("05-09"),
        "10-14": lambda: working_status_choice("10-14"),
        "15-19": lambda: working_status_choice("15-19"),
        "20-24": lambda: working_status_choice("20-24"),
        "25-29": lambda: working_status_choice("25-29"),
        "30-34": lambda: working_status_choice("30-34"),
        "35-39": lambda: working_status_choice("35-39"),
        "40-44": lambda: working_status_choice("40-49"),
        "45-49": lambda: working_status_choice("40-49"),
        "50-54": lambda: working_status_choice("50-59"),
        "55-59": lambda: working_status_choice("50-59"),
        "60-64": lambda: working_status_choice("60-69"),
        "65-69": lambda: working_status_choice("60-69"),
        "70-74": lambda: working_status_choice("70-79"),
        "75-79": lambda: working_status_choice("70-79"),
        "80+": lambda: working_status_choice("80+")
    }
    return age_to_work.get(age)()


def choose_pub_transport(working, public_transport_probability):
    if working:
        return np.random.choice(a=[True, False], p=[public_transport_probability, 1 - public_transport_probability])
    return False


if __name__ == "__main__":
    generate_population()
