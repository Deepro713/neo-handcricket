"""Generate country rosters for all remaining UN member states + observers.

Approach: regional/linguistic name pools (~30 of them). Each country is mapped
to a pool. The generator samples 33 unique given+family combos per country,
assigns roles per a fixed-shape squad template, writes JSON to
neo_handcricket/rosters/data/<slug>.json.

Run:
    python tools/generate_remaining_rosters.py
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

REPO_DATA = Path(__file__).resolve().parent.parent / "neo_handcricket/rosters/data"
REPO_DATA.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# Name pools per cultural / linguistic region.
# Each pool has ~30 given + ~30 family names. Convention is given-family unless
# stated otherwise. Names are *common, real* elements — not specific real
# people.
# -------------------------------------------------------------------------

POOLS: dict[str, dict] = {
    "germanic": {
        "given": ["Hans", "Klaus", "Werner", "Otto", "Friedrich", "Wilhelm", "Karl", "Ernst", "Heinrich", "Stefan", "Andreas", "Christian", "Lukas", "Maximilian", "Sebastian", "Markus", "Johannes", "Michael", "Florian", "Tobias", "Niklas", "Jonas", "Felix", "Leon", "Moritz", "Matthias", "Philip", "Konrad", "Ralf", "Dieter"],
        "family": ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann", "Schäfer", "Koch", "Bauer", "Richter", "Klein", "Wolf", "Schröder", "Neumann", "Schwarz", "Zimmermann", "Braun", "Krüger", "Hofmann", "Hartmann", "Lange", "Schmitt", "Werner", "Krause", "Lehmann", "König"],
        "convention": "given-family",
    },
    "french": {
        "given": ["Pierre", "Jean", "Louis", "Henri", "François", "André", "Philippe", "Michel", "Jacques", "Bernard", "Claude", "Marcel", "Antoine", "Christophe", "Olivier", "Sébastien", "Nicolas", "Vincent", "Julien", "Mathieu", "Florian", "Damien", "Thomas", "Pascal", "Romain", "Maxime", "Lucas", "Hugo", "Léo", "Bastien"],
        "family": ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier", "Morel", "Girard", "André", "Lefèvre", "Mercier", "Dupont", "Lambert", "Bonnet", "François", "Martinez"],
        "convention": "given-family",
    },
    "italian": {
        "given": ["Marco", "Luca", "Giulio", "Paolo", "Andrea", "Matteo", "Alessandro", "Francesco", "Giovanni", "Antonio", "Riccardo", "Davide", "Stefano", "Roberto", "Lorenzo", "Federico", "Salvatore", "Vincenzo", "Tommaso", "Simone", "Daniele", "Giuseppe", "Niccolò", "Pietro", "Emanuele", "Filippo", "Edoardo", "Christian", "Mattia", "Diego"],
        "family": ["Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo", "Ricci", "Marino", "Greco", "Bruno", "Gallo", "Conti", "De Luca", "Mancini", "Costa", "Giordano", "Rizzo", "Lombardi", "Moretti", "Barbieri", "Fontana", "Santoro", "Mariani", "Rinaldi", "Caruso", "Ferrara", "Galli", "Martini", "Leone"],
        "convention": "given-family",
    },
    "spanish": {
        "given": ["Antonio", "Manuel", "José", "Francisco", "David", "Juan", "Javier", "Daniel", "Carlos", "Jesús", "Miguel", "Alejandro", "Rafael", "Pablo", "Sergio", "Jorge", "Fernando", "Luis", "Alberto", "Álvaro", "Adrián", "Diego", "Iván", "Raúl", "Rubén", "Mario", "Iker", "Marcos", "Hugo", "Andrés"],
        "family": ["García", "Rodríguez", "González", "Fernández", "López", "Martínez", "Sánchez", "Pérez", "Gómez", "Martín", "Jiménez", "Ruiz", "Hernández", "Díaz", "Moreno", "Álvarez", "Muñoz", "Romero", "Alonso", "Gutiérrez", "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez", "Serrano", "Blanco", "Castillo"],
        "convention": "given-family",
    },
    "portuguese": {
        "given": ["João", "Pedro", "Miguel", "Tiago", "Rui", "André", "Diogo", "Francisco", "Bruno", "Hugo", "Ricardo", "Manuel", "Carlos", "Luís", "António", "Paulo", "Daniel", "Filipe", "Gonçalo", "Rafael", "Henrique", "Fábio", "Marco", "Vasco", "Tomás", "Duarte", "Afonso", "Bernardo", "Mateus", "Rodrigo"],
        "family": ["Silva", "Santos", "Ferreira", "Pereira", "Oliveira", "Costa", "Rodrigues", "Martins", "Jesus", "Sousa", "Fernandes", "Gonçalves", "Gomes", "Lopes", "Marques", "Alves", "Almeida", "Ribeiro", "Pinto", "Carvalho", "Teixeira", "Moreira", "Correia", "Mendes", "Nunes", "Soares", "Vieira", "Monteiro", "Cardoso", "Rocha"],
        "convention": "given-family",
    },
    "nordic": {
        "given": ["Erik", "Lars", "Anders", "Magnus", "Gustaf", "Olaf", "Bjørn", "Henrik", "Mikael", "Niklas", "Oscar", "Viktor", "Emil", "Linus", "Axel", "Sven", "Per", "Jan", "Karl", "Jonas", "Mattias", "Marcus", "Daniel", "Anton", "Hugo", "Ludvig", "Albin", "Filip", "Theodor", "Edvin"],
        "family": ["Andersson", "Johansson", "Karlsson", "Nilsson", "Eriksson", "Larsson", "Olsson", "Persson", "Svensson", "Gustafsson", "Pettersson", "Jonsson", "Jansson", "Hansson", "Bengtsson", "Jönsson", "Lindberg", "Jakobsson", "Magnusson", "Olofsson", "Lindström", "Lindqvist", "Lindgren", "Berg", "Axelsson", "Bergström", "Lundberg", "Lundgren", "Mattsson", "Lindholm"],
        "convention": "given-family",
    },
    "finnish": {
        "given": ["Mikko", "Jukka", "Antti", "Pekka", "Juhani", "Matti", "Timo", "Jari", "Hannu", "Markku", "Janne", "Sami", "Juha", "Jussi", "Petri", "Tuomas", "Lauri", "Olli", "Eero", "Mika", "Aleksi", "Niko", "Henri", "Joonas", "Toni", "Ville", "Eetu", "Tatu", "Tomi", "Aki"],
        "family": ["Korhonen", "Virtanen", "Mäkinen", "Nieminen", "Mäkelä", "Hämäläinen", "Laine", "Heikkinen", "Koskinen", "Järvinen", "Lehtonen", "Lehtinen", "Saarinen", "Salminen", "Heinonen", "Niemi", "Heikkilä", "Kinnunen", "Salonen", "Turunen", "Salo", "Laitinen", "Tuominen", "Rantanen", "Karjalainen", "Jokinen", "Mattila", "Savolainen", "Lahtinen", "Ahonen"],
        "convention": "given-family",
    },
    "baltic": {
        "given": ["Mārtiņš", "Jānis", "Andris", "Kārlis", "Edgars", "Roberts", "Aigars", "Gints", "Toms", "Raimonds", "Egidijus", "Mantas", "Lukas", "Marius", "Tomas", "Darius", "Andrius", "Saulius", "Audrius", "Algirdas", "Tarmo", "Marko", "Indrek", "Ants", "Priit", "Margus", "Rein", "Tõnu", "Mihkel", "Sander"],
        "family": ["Bērziņš", "Kalniņš", "Ozols", "Liepa", "Krūmiņš", "Vilks", "Zariņš", "Pērkons", "Žukauskas", "Kazlauskas", "Petrauskas", "Stankevičius", "Butkus", "Urbonas", "Vaitkus", "Tamm", "Saar", "Sepp", "Mägi", "Kask", "Kukk", "Rebane", "Ilves", "Pärn", "Kuusk", "Lepik", "Koppel", "Põder", "Adamson", "Hansen"],
        "convention": "given-family",
    },
    "slavic_east": {
        "given": ["Aleksandr", "Sergey", "Andrey", "Dmitry", "Mikhail", "Ivan", "Vladimir", "Pavel", "Maxim", "Nikolay", "Yuri", "Anton", "Roman", "Igor", "Oleg", "Konstantin", "Artem", "Denis", "Vasily", "Boris", "Valery", "Vladislav", "Ilya", "Stanislav", "Vyacheslav", "Yevgeny", "Kirill", "Leonid", "Anatoly", "Viktor"],
        "family": ["Ivanov", "Smirnov", "Kuznetsov", "Popov", "Vasiliev", "Petrov", "Sokolov", "Mikhailov", "Novikov", "Fedorov", "Morozov", "Volkov", "Alekseev", "Lebedev", "Semenov", "Yegorov", "Pavlov", "Kozlov", "Stepanov", "Nikolaev", "Orlov", "Andreev", "Makarov", "Nikitin", "Zakharov", "Zaitsev", "Solovyev", "Borisov", "Yakovlev", "Grigoriev"],
        "convention": "given-family",
    },
    "slavic_west": {
        "given": ["Jakub", "Mateusz", "Kacper", "Filip", "Michał", "Wojciech", "Krzysztof", "Tomasz", "Piotr", "Adam", "Marcin", "Paweł", "Maciej", "Dawid", "Łukasz", "Bartosz", "Jan", "Andrzej", "Stanisław", "Władysław", "Tadeusz", "Zbigniew", "Janusz", "Józef", "Antoni", "Aleksander", "Igor", "Karol", "Damian", "Grzegorz"],
        "family": ["Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński", "Lewandowski", "Zieliński", "Szymański", "Woźniak", "Dąbrowski", "Kozłowski", "Jankowski", "Mazur", "Kwiatkowski", "Krawczyk", "Piotrowski", "Grabowski", "Nowakowski", "Pawlak", "Michalski", "Nowicki", "Adamczyk", "Dudek", "Zając", "Wieczorek", "Jabłoński", "Król", "Majewski", "Olszewski"],
        "convention": "given-family",
    },
    "slavic_south": {
        "given": ["Marko", "Stefan", "Nikola", "Aleksandar", "Petar", "Milan", "Dušan", "Vladimir", "Filip", "Luka", "Jovan", "Boris", "Dejan", "Goran", "Branko", "Slobodan", "Zoran", "Milos", "Vuk", "Lazar", "Andrej", "Miroslav", "Dragan", "Nemanja", "Mihailo", "Radovan", "Predrag", "Bojan", "Saša", "Ivan"],
        "family": ["Petrović", "Jovanović", "Nikolić", "Marković", "Đorđević", "Stojanović", "Ilić", "Kostić", "Pavlović", "Mihailović", "Stanković", "Popović", "Janković", "Lazić", "Mladenović", "Ristić", "Tomić", "Bogdanović", "Stevanović", "Antić", "Horvat", "Knežević", "Kovačević", "Babić", "Marić", "Radović", "Đurić", "Vukić", "Stanić", "Aleksić"],
        "convention": "given-family",
    },
    "magyar": {
        "given": ["László", "István", "József", "János", "Zoltán", "Sándor", "Gábor", "Ferenc", "Tibor", "Tamás", "Attila", "András", "Péter", "Imre", "Béla", "Csaba", "Levente", "Bence", "Máté", "Kristóf", "Bálint", "Áron", "Marcell", "Dávid", "Ádám", "Gergő", "Zsolt", "Nándor", "Vilmos", "Antal"],
        "family": ["Nagy", "Kovács", "Tóth", "Szabó", "Horváth", "Varga", "Kiss", "Molnár", "Németh", "Farkas", "Balogh", "Papp", "Takács", "Juhász", "Lakatos", "Mészáros", "Oláh", "Simon", "Rácz", "Fekete", "Szilágyi", "Török", "Fehér", "Gál", "Balázs", "Kis", "Szűcs", "Király", "Katona", "Bíró"],
        "convention": "family-given",
    },
    "greek": {
        "given": ["Giorgos", "Nikos", "Dimitris", "Yiannis", "Kostas", "Michalis", "Christos", "Vasilis", "Andreas", "Stelios", "Petros", "Panagiotis", "Spyros", "Manolis", "Lefteris", "Stavros", "Antonis", "Apostolos", "Theodoros", "Athanasios", "Alexandros", "Pavlos", "Ilias", "Anastasios", "Charis", "Markos", "Filippos", "Aristotelis", "Konstantinos", "Achilleas"],
        "family": ["Papadopoulos", "Vlachos", "Karagiannis", "Konstantinidis", "Nikolaidis", "Antoniou", "Pappas", "Stavropoulos", "Christodoulou", "Theodorou", "Athanasiou", "Dimitriou", "Georgiou", "Markopoulos", "Petrou", "Spyrou", "Anastasiou", "Iliadis", "Manolakis", "Stergiou", "Demos", "Floros", "Lambros", "Vasileiou", "Polychroniou", "Sotiropoulos", "Tsiolakis", "Apostolopoulos", "Mavridis", "Diamantopoulos"],
        "convention": "given-family",
    },
    "turkish": {
        "given": ["Mehmet", "Mustafa", "Ahmet", "Ali", "Hüseyin", "Hasan", "İbrahim", "İsmail", "Osman", "Yusuf", "Murat", "Emre", "Burak", "Cem", "Serkan", "Tolga", "Onur", "Volkan", "Kemal", "Tarık", "Caner", "Selim", "Kerem", "Berk", "Eren", "Kaan", "Doğan", "Furkan", "Bora", "Yiğit"],
        "family": ["Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Yıldız", "Yıldırım", "Öztürk", "Aydın", "Özdemir", "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt", "Özkan", "Şimşek", "Polat", "Korkmaz", "Çakır", "Erdoğan", "Aksoy", "Türk", "Tekin", "Bulut", "Acar", "Avcı"],
        "convention": "given-family",
    },
    "arab": {
        "given": ["Mohammed", "Ahmed", "Ali", "Hassan", "Hussein", "Omar", "Khalid", "Abdullah", "Saeed", "Faisal", "Tariq", "Yusuf", "Ibrahim", "Ismail", "Mahmoud", "Mansour", "Nasser", "Rashid", "Salem", "Salim", "Walid", "Yasin", "Zaki", "Adel", "Bilal", "Fadi", "Karim", "Marwan", "Samir", "Wassim"],
        "family": ["Al-Hassan", "Al-Mansour", "Al-Sayed", "Al-Khalil", "Al-Faisal", "Al-Rashid", "Al-Hadi", "Al-Saud", "Al-Maktoum", "Al-Sabah", "Al-Thani", "Al-Wahab", "Khoury", "Mansour", "Haddad", "Sayegh", "Karam", "Tahir", "Najjar", "Salem", "Ibrahim", "Hassan", "Sharif", "Bishara", "Aziz", "Farouk", "Nassar", "Najib", "Habib", "Bakri"],
        "convention": "given-family",
    },
    "persian": {
        "given": ["Ali", "Reza", "Hassan", "Hossein", "Mohammad", "Majid", "Behrouz", "Farhad", "Kourosh", "Saeed", "Bahram", "Amir", "Arman", "Pouya", "Sina", "Soroush", "Babak", "Kian", "Cyrus", "Darius", "Navid", "Mehrdad", "Shahin", "Pejman", "Hooman", "Ramin", "Ardalan", "Bardia", "Kambiz", "Yashar"],
        "family": ["Mohammadi", "Hosseini", "Rezaei", "Karimi", "Akbari", "Ahmadi", "Hashemi", "Sharifi", "Najafi", "Salehi", "Jafari", "Ebrahimi", "Rahimi", "Naderi", "Tabatabai", "Sadeghi", "Yousefi", "Ghasemi", "Mahmoudi", "Asghari", "Bagheri", "Alavi", "Arabi", "Behzadi", "Daneshvar", "Esfahani", "Farahani", "Ghaffari", "Kazemi", "Mansouri"],
        "convention": "given-family",
    },
    "hebrew": {
        "given": ["David", "Yossi", "Avi", "Eitan", "Yair", "Asher", "Itai", "Noam", "Lior", "Roi", "Tomer", "Yotam", "Amir", "Ofer", "Shimon", "Eyal", "Gilad", "Ronen", "Eldad", "Idan", "Tal", "Boaz", "Daniel", "Yonatan", "Yehuda", "Moshe", "Doron", "Maor", "Gal", "Itamar"],
        "family": ["Cohen", "Levi", "Mizrahi", "Peretz", "Friedman", "Avraham", "Dahan", "Biton", "Azulay", "Malka", "Hayoun", "Amar", "Shalom", "Bar-On", "Goldstein", "Rosenberg", "Eshed", "Shapira", "Ben-David", "Gabai", "Yosef", "Ezra", "Carmon", "Shaked", "Erez", "Lev", "Kaplan", "Segal", "Ben-Ari", "Bachar"],
        "convention": "given-family",
    },
    "central_asian": {
        "given": ["Bakhtiyar", "Ruslan", "Timur", "Azamat", "Daniyar", "Aibek", "Kanat", "Nurbol", "Marat", "Yerlan", "Erbol", "Abay", "Bakyt", "Murat", "Nurlan", "Sanjar", "Bekbolat", "Ulugbek", "Otabek", "Anvar", "Akmal", "Davron", "Sherzod", "Jamol", "Rustam", "Ilkhom", "Doniyor", "Bobur", "Khurshid", "Sardor"],
        "family": ["Aliyev", "Mukhamedov", "Toktarov", "Akhmetov", "Bekov", "Yusupov", "Ergashev", "Karimov", "Rasulov", "Tursunov", "Nazarov", "Ismailov", "Saidov", "Khodjayev", "Yuldashev", "Murodov", "Sobirov", "Madaminov", "Nematov", "Rakhimov", "Iskakov", "Suleimenov", "Omarov", "Kasymov", "Bekzhanov", "Erbolov", "Asanov", "Tashtemirov", "Imankulov", "Karpov"],
        "convention": "given-family",
    },
    "caucasian": {
        "given": ["Giorgi", "Nikoloz", "Levan", "Davit", "Irakli", "Zurab", "Tornike", "Vakhtang", "Beso", "Otar", "Aram", "Hovhannes", "Tigran", "Vahan", "Gor", "Karen", "Armen", "Sargis", "Hayk", "Ashot", "Rashad", "Ilkin", "Elnur", "Kamran", "Ramin", "Vusal", "Anar", "Tural", "Farid", "Nijat"],
        "family": ["Beridze", "Kapanadze", "Maisuradze", "Giorgadze", "Lomidze", "Tsiklauri", "Khelaia", "Bakradze", "Kvirikashvili", "Tabidze", "Hovhannisyan", "Grigoryan", "Sargsyan", "Petrosyan", "Avetisyan", "Harutyunyan", "Stepanyan", "Khachatryan", "Mkrtchyan", "Mnatsakanyan", "Aliyev", "Mammadov", "Hasanov", "Huseynov", "Babayev", "Rzayev", "Karimov", "Ahmadov", "Suleimanov", "Quliyev"],
        "convention": "given-family",
    },
    "east_african": {
        "given": ["Daudi", "Yusuf", "Hassan", "Juma", "Bakari", "Salim", "Mwangi", "Kamau", "Kipchoge", "Otieno", "Wanjiku", "Ochieng", "Kiprop", "Mutua", "Njoroge", "Onyango", "Mukasa", "Kakuru", "Twesigye", "Habimana", "Niyonzima", "Kamana", "Ndayisaba", "Tumusiime", "Kayiranga", "Kanyamuneza", "Asha", "Hamisi", "Kassim", "Idrissa"],
        "family": ["Kamau", "Mwangi", "Otieno", "Wanjiku", "Onyango", "Kipchoge", "Kiprop", "Ochieng", "Njoroge", "Mutua", "Mukasa", "Sserwanga", "Habimana", "Nyirahabimana", "Niyonzima", "Kanyamuneza", "Mwakikagile", "Mtetwa", "Mwambazi", "Said", "Hassan", "Hamisi", "Bakari", "Juma", "Yusuf", "Mohamed", "Tumusiime", "Twesigye", "Mugisha", "Kakuru"],
        "convention": "given-family",
    },
    "west_african": {
        "given": ["Kwame", "Kofi", "Kwesi", "Kojo", "Yaw", "Akwasi", "Mensah", "Kwabena", "Adjei", "Boateng", "Chukwuma", "Chinedu", "Emeka", "Obi", "Adebayo", "Olusegun", "Tunde", "Babatunde", "Femi", "Kunle", "Mamadou", "Ousmane", "Ibrahim", "Souleymane", "Cheikh", "Modou", "Pape", "Abdoulaye", "Aliou", "Moussa"],
        "family": ["Mensah", "Boateng", "Asante", "Owusu", "Adjei", "Agyemang", "Frimpong", "Nkrumah", "Sarpong", "Yeboah", "Okonkwo", "Adeyemi", "Adesanya", "Olawale", "Bamgboye", "Ojo", "Oyelaran", "Igwe", "Eze", "Okeke", "Diallo", "Diop", "Ndiaye", "Fall", "Sow", "Cissé", "Sy", "Ba", "Niang", "Sylla"],
        "convention": "given-family",
    },
    "horn_african": {
        "given": ["Tewodros", "Yohannes", "Dawit", "Yonas", "Bereket", "Hailu", "Mulugeta", "Tesfaye", "Solomon", "Girma", "Kebede", "Abel", "Berhanu", "Endale", "Fitsum", "Mekonnen", "Selamawit", "Teshome", "Wondimu", "Daniel", "Mahdi", "Ahmed", "Farah", "Hassan", "Abdi", "Mohamed", "Said", "Yusuf", "Ismail", "Omar"],
        "family": ["Bekele", "Tadesse", "Hailemariam", "Tesfaye", "Mengistu", "Gebremedhin", "Haile", "Tekle", "Mekonnen", "Asfaw", "Wolde", "Girma", "Tewolde", "Negash", "Yohannes", "Gebreyesus", "Tsegaye", "Demeke", "Birhanu", "Alemu", "Mohamud", "Abdirahman", "Farah", "Hassan", "Ali", "Adan", "Yusuf", "Mohamed", "Said", "Hussein"],
        "convention": "given-family",
    },
    "southern_african": {
        "given": ["Sipho", "Bongani", "Themba", "Nkosi", "Lwazi", "Khaya", "Sandile", "Bonga", "Lwandle", "Thando", "Mpho", "Tebogo", "Tshepo", "Sello", "Lerato", "Karabo", "Tsepiso", "Lehlohonolo", "Bafana", "Sibusiso", "Tafadzwa", "Tendai", "Tinashe", "Farai", "Munashe", "Kagiso", "Itumeleng", "Refilwe", "Bokang", "Tumelo"],
        "family": ["Dlamini", "Mokoena", "Khumalo", "Ngubane", "Zulu", "Mhlongo", "Madondo", "Sithole", "Tshabalala", "Ndlovu", "Nkosi", "Buthelezi", "Mthembu", "Mahlangu", "Mabaso", "Maseko", "Moyo", "Sibanda", "Ncube", "Dube", "Banda", "Mwamba", "Phiri", "Tembo", "Daka", "Nkomo", "Magagula", "Dlamini", "Shongwe", "Ngwenya"],
        "convention": "given-family",
    },
    "east_asian_chinese": {
        "given": ["Wei", "Lei", "Bo", "Hao", "Jun", "Yu", "Tao", "Lin", "Long", "Ming", "Yong", "Qiang", "Xiang", "Zheng", "Hui", "Chao", "Bin", "Gang", "Feng", "Liang", "Yan", "Jian", "Kai", "Cheng", "Peng", "Hua", "Bo", "Yi", "Xin", "Jie"],
        "family": ["Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu", "Zhou", "Xu", "Sun", "Ma", "Zhu", "Hu", "Guo", "He", "Lin", "Gao", "Luo", "Liang", "Song", "Zheng", "Xie", "Han", "Tang", "Feng", "Yu", "Dong", "Cao"],
        "convention": "family-given",
    },
    "east_asian_korean": {
        "given": ["Min-jun", "Seo-jun", "Do-yun", "Ha-jun", "Si-woo", "Joo-won", "Ji-ho", "Yu-jun", "Eun-woo", "Geon-woo", "Hyun-woo", "Ji-hoon", "Sung-min", "Tae-yang", "Jae-young", "Min-seok", "Seung-hyun", "Sang-min", "Dong-hyun", "Ki-hwan", "Jung-ho", "Hyun-bin", "Kyung-tae", "Hyo-jin", "Yong-su", "Jin-young", "Hae-il", "Bo-gum", "Ji-sub", "Jong-hyun"],
        "family": ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Cho", "Yoon", "Jang", "Lim", "Han", "Oh", "Seo", "Shin", "Kwon", "Hwang", "Ahn", "Song", "Yoo", "Hong", "Jeon", "Ko", "Moon", "Yang", "Son", "Bae", "Baek", "Heo", "Nam", "Sim"],
        "convention": "family-given",
    },
    "east_asian_mongolian": {
        "given": ["Bat-Erdene", "Munkhbat", "Tumur", "Ganbat", "Bayar", "Erdene", "Davaa", "Buyant", "Tsogt", "Khishig", "Naran", "Otgonbayar", "Munkhsaikhan", "Saikhanbileg", "Tsogtbaatar", "Battulga", "Khaltmaa", "Sukhbaatar", "Enkhbat", "Ariunbold", "Ganzorig", "Munkhjargal", "Bilguun", "Temuujin", "Chinbat", "Dorj", "Bayasgalan", "Otgonsuren", "Erdenebileg", "Boldbaatar"],
        "family": ["Batbayar", "Munkhbayar", "Bayasgalan", "Erdenechimeg", "Tserendorj", "Ganbaatar", "Davaadorj", "Tsogtbaatar", "Buyantogtokh", "Otgonbayar", "Chimedtseren", "Dashdorj", "Naranbat", "Bayartsogt", "Sukhbat", "Erdenebileg", "Khorloo", "Sosor", "Battushig", "Munkhdalai", "Enkhjargal", "Lkhagvasuren", "Ariunsaikhan", "Tumendelger", "Bayanzul", "Yundenbat", "Sodbileg", "Tsendsuren", "Dolgor", "Tuvshintugs"],
        "convention": "given-family",
    },
    "southeast_asian_thai": {
        "given": ["Somchai", "Somsak", "Suchart", "Surasak", "Thawatchai", "Wichai", "Anan", "Chaiyaporn", "Krit", "Niran", "Phanuwat", "Pongthep", "Prawit", "Rachan", "Sakda", "Sunan", "Tanin", "Thanawat", "Vichai", "Yuthana", "Boonsong", "Chalerm", "Det", "Ekkapan", "Jirayu", "Kanya", "Manop", "Narongchai", "Ongart", "Phisut"],
        "family": ["Wongsawat", "Suthep", "Thaksin", "Phromphan", "Saengsawang", "Ratchadaphisek", "Phongpaichit", "Saiyud", "Worawit", "Charoensuk", "Sukhumvit", "Krasae", "Boonchu", "Jaidee", "Niwat", "Aroon", "Chaichana", "Phuangmalai", "Sangkhachan", "Bunyasarn", "Surasak", "Kantapong", "Suwannarat", "Phongthep", "Charunyasak", "Wongsuwan", "Saksithikarn", "Krittipong", "Chanchaisak", "Thawatchai"],
        "convention": "given-family",
    },
    "southeast_asian_vietnamese": {
        "given": ["Anh", "Bao", "Binh", "Cao", "Cuong", "Dung", "Duy", "Hai", "Hoang", "Hung", "Khang", "Khoa", "Long", "Manh", "Minh", "Nam", "Phong", "Quang", "Quoc", "Son", "Tai", "Tan", "Thanh", "Toan", "Trung", "Tuan", "Tung", "Vinh", "Vu", "Hieu"],
        "family": ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Phan", "Vu", "Vo", "Dang", "Bui", "Do", "Ho", "Ngo", "Duong", "Ly", "Truong", "Cao", "Mai", "Lam", "Tang", "Thai", "Dinh", "Doan", "Kieu", "Lam", "Lieu", "Luong", "Lai", "Cu", "Tu"],
        "convention": "family-given",
    },
    "southeast_asian_burmese": {
        "given": ["Aung", "Min", "Kyaw", "Zaw", "Soe", "Thet", "Tun", "Maung", "Phyo", "Hein", "Kaung", "Naing", "Wai", "Yadana", "Thant", "Myo", "Ko", "Thiha", "Bo", "Nay", "Aung Min", "Zaw Min", "Tun Tun", "Soe Naing", "Hla", "Khin", "Myint", "Win", "San", "Lin"],
        "family": ["Aung", "Min", "Soe", "Tun", "Maung", "Hein", "Phyo", "Kyaw", "Win", "Myint", "Hla", "Khin", "San", "Thant", "Naing", "Yadana", "Thiha", "Lin", "Pyone", "Wai", "Zaw", "Myo", "Ko", "Bo", "Nay", "Yan", "Mya", "Nu", "Cho", "Aye"],
        "convention": "given-family",
    },
    "southeast_asian_malay": {
        "given": ["Ahmad", "Mohd", "Hafiz", "Rizal", "Faizal", "Aiman", "Daniyal", "Hakim", "Iqbal", "Khairul", "Luqman", "Naufal", "Razak", "Shafiq", "Zulkifli", "Adi", "Bakri", "Cahyo", "Dewa", "Eko", "Fajar", "Galih", "Hadi", "Indra", "Joko", "Kurniawan", "Lutfi", "Made", "Nugroho", "Pradana"],
        "family": ["Bin Ibrahim", "Bin Hassan", "Bin Yusuf", "Bin Razak", "Bin Mohamad", "Bin Salleh", "Bin Aziz", "Bin Hashim", "Bin Ismail", "Bin Said", "Suharto", "Wijaya", "Pratama", "Saputra", "Hidayat", "Setiawan", "Nugroho", "Susanto", "Lukman", "Wibowo", "Iskandar", "Halim", "Zulkifli", "Mansur", "Tan", "Lim", "Wong", "Goh", "Tang", "Soh"],
        "convention": "given-family",
    },
    "southeast_asian_filipino": {
        "given": ["Juan", "Jose", "Pedro", "Antonio", "Manuel", "Carlos", "Ramon", "Eduardo", "Francisco", "Roberto", "Andres", "Mateo", "Luis", "Miguel", "Diego", "Rafael", "Gabriel", "Daniel", "Marco", "Paolo", "Ricardo", "Vicente", "Salvador", "Renato", "Romulo", "Wilfredo", "Jaime", "Edmundo", "Ferdinand", "Eligio"],
        "family": ["Santos", "Reyes", "Cruz", "Bautista", "Garcia", "Mendoza", "Ramos", "Aquino", "Diaz", "Castillo", "Gonzales", "Tolentino", "Hernandez", "Pineda", "Villanueva", "Salazar", "Mercado", "Ramirez", "Aguilar", "Velasco", "Padilla", "Domingo", "Cabrera", "Andrada", "Salonga", "Tagalog", "Maglinao", "Macapagal", "Lopez", "Magsaysay"],
        "convention": "given-family",
    },
    "south_asian_dzongkha": {
        "given": ["Dorji", "Tashi", "Pema", "Karma", "Sonam", "Tshering", "Phuntsho", "Wangchuk", "Namgay", "Rinzin", "Yeshey", "Ugyen", "Jigme", "Kinley", "Tenzin", "Phurba", "Singye", "Lhaden", "Choden", "Dechen", "Norbu", "Pasang", "Lobsang", "Thinley", "Gyeltshen", "Tobgay", "Kuenzang", "Sherab", "Drukpa", "Wangmo"],
        "family": ["Dorji", "Wangchuk", "Tshering", "Namgay", "Pema", "Tashi", "Karma", "Phuntsho", "Sonam", "Rinzin", "Norbu", "Yeshey", "Tenzin", "Jigme", "Kinley", "Phurba", "Lhaden", "Choden", "Dechen", "Wangmo", "Singye", "Lobsang", "Thinley", "Gyeltshen", "Tobgay", "Kuenzang", "Sherab", "Drukpa", "Pasang", "Ugyen"],
        "convention": "given-family",
    },
    "south_asian_dhivehi": {
        "given": ["Ali", "Ahmed", "Mohamed", "Ibrahim", "Hassan", "Hussain", "Adam", "Yoosuf", "Ismail", "Imran", "Faisal", "Khaleel", "Mahir", "Riyaz", "Saeed", "Suhail", "Thariq", "Waheed", "Yameen", "Zahid", "Areef", "Bashir", "Dhonbeyya", "Easa", "Fareed", "Ghassan", "Haaroon", "Imad", "Jameel", "Kareem"],
        "family": ["Didi", "Naseem", "Rasheed", "Saleem", "Shafeeg", "Waheed", "Latheef", "Mohamed", "Ibrahim", "Ali", "Hassan", "Hussain", "Adam", "Yoosuf", "Faisal", "Imran", "Riyaz", "Saeed", "Thariq", "Yameen", "Zahid", "Bashir", "Easa", "Fareed", "Manik", "Kaleem", "Naazim", "Ramiz", "Shameem", "Wajeeh"],
        "convention": "given-family",
    },
    "anglo_canadian": {
        "given": ["Liam", "Noah", "Oliver", "William", "Benjamin", "Lucas", "Henry", "Alexander", "Mason", "Ethan", "Jacob", "Jackson", "Owen", "James", "Daniel", "Connor", "Ryan", "Dylan", "Tyler", "Carson", "Brayden", "Gavin", "Logan", "Cooper", "Hunter", "Wyatt", "Hudson", "Brody", "Landon", "Easton"],
        "family": ["Smith", "Brown", "Tremblay", "Martin", "Roy", "Wilson", "MacDonald", "Gagnon", "Johnson", "Taylor", "Anderson", "Lee", "White", "Williams", "Davis", "Thompson", "Campbell", "Bouchard", "Côté", "Beaulieu", "Lefebvre", "Caron", "Bélanger", "Pelletier", "Lavoie", "Fortin", "Gauthier", "Boucher", "Morin", "Lapointe"],
        "convention": "given-family",
    },
    "iberian_latam": {
        "given": ["Carlos", "Juan", "Diego", "Andrés", "Miguel", "Sebastián", "Mateo", "Santiago", "Nicolás", "Felipe", "Daniel", "David", "Alejandro", "Cristian", "Esteban", "Fabián", "Gabriel", "Hernán", "Iván", "Joaquín", "Luis", "Manuel", "Octavio", "Pablo", "Rafael", "Sergio", "Tomás", "Víctor", "Xavier", "Yago"],
        "family": ["González", "Rodríguez", "Pérez", "Sánchez", "Ramírez", "Cruz", "Flores", "Gómez", "Morales", "Torres", "Vásquez", "Castro", "Ortega", "Núñez", "Aguilar", "Salazar", "Mendoza", "Reyes", "Ramos", "Vargas", "Romero", "Sosa", "Acosta", "Cabrera", "Medina", "Silva", "Herrera", "Núñez", "Espinoza", "Jiménez"],
        "convention": "given-family",
    },
    "portuguese_latam": {
        "given": ["João", "Pedro", "Lucas", "Gabriel", "Matheus", "Rafael", "Felipe", "Bruno", "Daniel", "Diego", "Carlos", "Marcos", "Vinícius", "Thiago", "Caio", "Eduardo", "Fernando", "Henrique", "Igor", "Júlio", "Leandro", "Marcelo", "Nelson", "Otávio", "Paulo", "Rodrigo", "Samuel", "Tomás", "Victor", "Wesley"],
        "family": ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Almeida", "Costa", "Pereira", "Lima", "Carvalho", "Ribeiro", "Martins", "Araújo", "Gomes", "Barbosa", "Cardoso", "Mendes", "Rocha", "Dias", "Pinto", "Vieira", "Moreira", "Nascimento", "Teixeira", "Sousa", "Cunha", "Cavalcanti", "Castro", "Correia"],
        "convention": "given-family",
    },
    "caribbean": {
        "given": ["Andre", "Kemar", "Dwayne", "Jermaine", "Rohan", "Akeem", "Devon", "Marlon", "Shamarh", "Roston", "Sunil", "Imran", "Nicholas", "Devendra", "Saheed", "Carlos", "Brandon", "Kyle", "Marquino", "Jamaal", "Tristan", "Andre", "Garfield", "Carlton", "Raheem", "Alvin", "Renaldo", "Danza", "Vincent", "Wayne"],
        "family": ["Holder", "Bynoe", "Forde", "King", "Phillip", "Lewis", "Brathwaite", "Walsh", "Powell", "Williams", "Bishop", "Mayers", "Marshall", "Smith", "Stuart", "Carter", "Springer", "Stoute", "Hoyte", "Pierre", "Layne", "Sandford", "Worrell", "Catlyn", "Babb", "Yearwood", "Calliste", "Boodram", "Ramnarine", "Singh"],
        "convention": "given-family",
    },
    "pacific_islander": {
        "given": ["Tevita", "Sione", "Manu", "Rua", "Kele", "Filipe", "Tomu", "Mosese", "Apolosi", "Etuate", "Jone", "Ratu", "Sakaria", "Akeli", "Inoke", "Lopeti", "Maika", "Naipote", "Osea", "Pita", "Saula", "Tanieli", "Vatu", "Waisake", "Eroni", "Faiosi", "Henele", "Iliesa", "Joeli", "Karalo"],
        "family": ["Tupou", "Vakatale", "Ratuva", "Naivaluwaqa", "Cakacaka", "Daunivalu", "Fifita", "Hala", "Inia", "Jione", "Kava", "Latu", "Maumi", "Niumataiwalu", "Otogo", "Pole", "Qaqa", "Rabuka", "Salabogi", "Tabua", "Uate", "Vakatawa", "Wakanivalu", "Yabaki", "Zalewski", "Aholelei", "Botofau", "Cakau", "Dakuwaqa", "Etika"],
        "convention": "given-family",
    },
}


# -------------------------------------------------------------------------
# Country → pool mapping (~177 countries).
# Format: slug -> {"name", "flag", "pool"}
# -------------------------------------------------------------------------

COUNTRIES: dict[str, dict] = {
    # Already done — skip these (listed for sanity check):
    # india, england, australia, pakistan, south-africa, new-zealand,
    # sri-lanka, bangladesh, zimbabwe, afghanistan, ireland, west-indies,
    # japan, antarctica, scotland, netherlands, nepal, usa

    # Europe
    "germany":              {"name": "Germany",              "flag": "🇩🇪", "pool": "germanic"},
    "austria":              {"name": "Austria",              "flag": "🇦🇹", "pool": "germanic"},
    "switzerland":          {"name": "Switzerland",          "flag": "🇨🇭", "pool": "germanic"},
    "liechtenstein":        {"name": "Liechtenstein",        "flag": "🇱🇮", "pool": "germanic"},
    "luxembourg":           {"name": "Luxembourg",           "flag": "🇱🇺", "pool": "germanic"},
    "france":               {"name": "France",               "flag": "🇫🇷", "pool": "french"},
    "belgium":              {"name": "Belgium",              "flag": "🇧🇪", "pool": "french"},
    "monaco":               {"name": "Monaco",               "flag": "🇲🇨", "pool": "french"},
    "italy":                {"name": "Italy",                "flag": "🇮🇹", "pool": "italian"},
    "san-marino":           {"name": "San Marino",           "flag": "🇸🇲", "pool": "italian"},
    "vatican-city":         {"name": "Vatican City",         "flag": "🇻🇦", "pool": "italian"},
    "spain":                {"name": "Spain",                "flag": "🇪🇸", "pool": "spanish"},
    "andorra":              {"name": "Andorra",              "flag": "🇦🇩", "pool": "spanish"},
    "portugal":             {"name": "Portugal",             "flag": "🇵🇹", "pool": "portuguese"},
    "sweden":               {"name": "Sweden",               "flag": "🇸🇪", "pool": "nordic"},
    "norway":               {"name": "Norway",               "flag": "🇳🇴", "pool": "nordic"},
    "denmark":              {"name": "Denmark",              "flag": "🇩🇰", "pool": "nordic"},
    "iceland":              {"name": "Iceland",              "flag": "🇮🇸", "pool": "nordic"},
    "finland":              {"name": "Finland",              "flag": "🇫🇮", "pool": "finnish"},
    "estonia":              {"name": "Estonia",              "flag": "🇪🇪", "pool": "baltic"},
    "latvia":               {"name": "Latvia",               "flag": "🇱🇻", "pool": "baltic"},
    "lithuania":            {"name": "Lithuania",            "flag": "🇱🇹", "pool": "baltic"},
    "russia":               {"name": "Russia",               "flag": "🇷🇺", "pool": "slavic_east"},
    "ukraine":              {"name": "Ukraine",              "flag": "🇺🇦", "pool": "slavic_east"},
    "belarus":              {"name": "Belarus",              "flag": "🇧🇾", "pool": "slavic_east"},
    "moldova":              {"name": "Moldova",              "flag": "🇲🇩", "pool": "slavic_east"},
    "poland":               {"name": "Poland",               "flag": "🇵🇱", "pool": "slavic_west"},
    "czech-republic":       {"name": "Czech Republic",       "flag": "🇨🇿", "pool": "slavic_west"},
    "slovakia":             {"name": "Slovakia",             "flag": "🇸🇰", "pool": "slavic_west"},
    "hungary":              {"name": "Hungary",              "flag": "🇭🇺", "pool": "magyar"},
    "romania":              {"name": "Romania",              "flag": "🇷🇴", "pool": "slavic_south"},
    "bulgaria":             {"name": "Bulgaria",             "flag": "🇧🇬", "pool": "slavic_south"},
    "slovenia":             {"name": "Slovenia",             "flag": "🇸🇮", "pool": "slavic_south"},
    "croatia":              {"name": "Croatia",              "flag": "🇭🇷", "pool": "slavic_south"},
    "bosnia-and-herzegovina":{"name":"Bosnia and Herzegovina","flag":"🇧🇦","pool":"slavic_south"},
    "serbia":               {"name": "Serbia",               "flag": "🇷🇸", "pool": "slavic_south"},
    "montenegro":           {"name": "Montenegro",           "flag": "🇲🇪", "pool": "slavic_south"},
    "north-macedonia":      {"name": "North Macedonia",      "flag": "🇲🇰", "pool": "slavic_south"},
    "albania":              {"name": "Albania",              "flag": "🇦🇱", "pool": "slavic_south"},
    "kosovo":               {"name": "Kosovo",               "flag": "🇽🇰", "pool": "slavic_south"},
    "greece":               {"name": "Greece",               "flag": "🇬🇷", "pool": "greek"},
    "cyprus":               {"name": "Cyprus",               "flag": "🇨🇾", "pool": "greek"},
    "malta":                {"name": "Malta",                "flag": "🇲🇹", "pool": "italian"},
    "turkey":               {"name": "Turkey",               "flag": "🇹🇷", "pool": "turkish"},

    # Middle East
    "israel":               {"name": "Israel",               "flag": "🇮🇱", "pool": "hebrew"},
    "palestine":            {"name": "Palestine",            "flag": "🇵🇸", "pool": "arab"},
    "jordan":               {"name": "Jordan",               "flag": "🇯🇴", "pool": "arab"},
    "lebanon":              {"name": "Lebanon",              "flag": "🇱🇧", "pool": "arab"},
    "syria":                {"name": "Syria",                "flag": "🇸🇾", "pool": "arab"},
    "iraq":                 {"name": "Iraq",                 "flag": "🇮🇶", "pool": "arab"},
    "iran":                 {"name": "Iran",                 "flag": "🇮🇷", "pool": "persian"},
    "saudi-arabia":         {"name": "Saudi Arabia",         "flag": "🇸🇦", "pool": "arab"},
    "uae":                  {"name": "UAE",                  "flag": "🇦🇪", "pool": "arab"},
    "oman":                 {"name": "Oman",                 "flag": "🇴🇲", "pool": "arab"},
    "qatar":                {"name": "Qatar",                "flag": "🇶🇦", "pool": "arab"},
    "bahrain":              {"name": "Bahrain",              "flag": "🇧🇭", "pool": "arab"},
    "kuwait":               {"name": "Kuwait",               "flag": "🇰🇼", "pool": "arab"},
    "yemen":                {"name": "Yemen",                "flag": "🇾🇪", "pool": "arab"},

    # North Africa
    "egypt":                {"name": "Egypt",                "flag": "🇪🇬", "pool": "arab"},
    "libya":                {"name": "Libya",                "flag": "🇱🇾", "pool": "arab"},
    "tunisia":              {"name": "Tunisia",              "flag": "🇹🇳", "pool": "arab"},
    "algeria":              {"name": "Algeria",              "flag": "🇩🇿", "pool": "arab"},
    "morocco":              {"name": "Morocco",              "flag": "🇲🇦", "pool": "arab"},
    "mauritania":           {"name": "Mauritania",           "flag": "🇲🇷", "pool": "arab"},
    "sudan":                {"name": "Sudan",                "flag": "🇸🇩", "pool": "arab"},
    "south-sudan":          {"name": "South Sudan",          "flag": "🇸🇸", "pool": "east_african"},

    # Sub-Saharan Africa
    "nigeria":              {"name": "Nigeria",              "flag": "🇳🇬", "pool": "west_african"},
    "ghana":                {"name": "Ghana",                "flag": "🇬🇭", "pool": "west_african"},
    "senegal":              {"name": "Senegal",              "flag": "🇸🇳", "pool": "west_african"},
    "cote-divoire":         {"name": "Côte d'Ivoire",        "flag": "🇨🇮", "pool": "west_african"},
    "mali":                 {"name": "Mali",                 "flag": "🇲🇱", "pool": "west_african"},
    "burkina-faso":         {"name": "Burkina Faso",         "flag": "🇧🇫", "pool": "west_african"},
    "niger":                {"name": "Niger",                "flag": "🇳🇪", "pool": "west_african"},
    "guinea":               {"name": "Guinea",               "flag": "🇬🇳", "pool": "west_african"},
    "sierra-leone":         {"name": "Sierra Leone",         "flag": "🇸🇱", "pool": "west_african"},
    "liberia":              {"name": "Liberia",              "flag": "🇱🇷", "pool": "west_african"},
    "togo":                 {"name": "Togo",                 "flag": "🇹🇬", "pool": "west_african"},
    "benin":                {"name": "Benin",                "flag": "🇧🇯", "pool": "west_african"},
    "cameroon":             {"name": "Cameroon",             "flag": "🇨🇲", "pool": "west_african"},
    "gambia":               {"name": "The Gambia",           "flag": "🇬🇲", "pool": "west_african"},
    "cape-verde":           {"name": "Cape Verde",           "flag": "🇨🇻", "pool": "portuguese"},
    "guinea-bissau":        {"name": "Guinea-Bissau",        "flag": "🇬🇼", "pool": "portuguese"},
    "equatorial-guinea":    {"name": "Equatorial Guinea",    "flag": "🇬🇶", "pool": "iberian_latam"},
    "sao-tome-and-principe":{"name": "São Tomé and Príncipe","flag": "🇸🇹", "pool": "portuguese"},
    "chad":                 {"name": "Chad",                 "flag": "🇹🇩", "pool": "arab"},
    "central-african-republic":{"name":"Central African Republic","flag":"🇨🇫","pool":"french"},
    "ethiopia":             {"name": "Ethiopia",             "flag": "🇪🇹", "pool": "horn_african"},
    "eritrea":              {"name": "Eritrea",              "flag": "🇪🇷", "pool": "horn_african"},
    "djibouti":             {"name": "Djibouti",             "flag": "🇩🇯", "pool": "horn_african"},
    "somalia":              {"name": "Somalia",              "flag": "🇸🇴", "pool": "horn_african"},
    "kenya":                {"name": "Kenya",                "flag": "🇰🇪", "pool": "east_african"},
    "tanzania":             {"name": "Tanzania",             "flag": "🇹🇿", "pool": "east_african"},
    "uganda":               {"name": "Uganda",               "flag": "🇺🇬", "pool": "east_african"},
    "rwanda":               {"name": "Rwanda",               "flag": "🇷🇼", "pool": "east_african"},
    "burundi":              {"name": "Burundi",              "flag": "🇧🇮", "pool": "east_african"},
    "namibia":              {"name": "Namibia",              "flag": "🇳🇦", "pool": "southern_african"},
    "botswana":             {"name": "Botswana",             "flag": "🇧🇼", "pool": "southern_african"},
    "lesotho":              {"name": "Lesotho",              "flag": "🇱🇸", "pool": "southern_african"},
    "eswatini":             {"name": "Eswatini",             "flag": "🇸🇿", "pool": "southern_african"},
    "mozambique":           {"name": "Mozambique",           "flag": "🇲🇿", "pool": "portuguese"},
    "madagascar":           {"name": "Madagascar",           "flag": "🇲🇬", "pool": "french"},
    "mauritius":            {"name": "Mauritius",            "flag": "🇲🇺", "pool": "french"},
    "seychelles":           {"name": "Seychelles",           "flag": "🇸🇨", "pool": "french"},
    "comoros":              {"name": "Comoros",              "flag": "🇰🇲", "pool": "arab"},
    "malawi":               {"name": "Malawi",               "flag": "🇲🇼", "pool": "southern_african"},
    "zambia":               {"name": "Zambia",               "flag": "🇿🇲", "pool": "southern_african"},
    "angola":               {"name": "Angola",               "flag": "🇦🇴", "pool": "portuguese"},
    "drc":                  {"name": "DR Congo",             "flag": "🇨🇩", "pool": "french"},
    "congo":                {"name": "Republic of the Congo","flag": "🇨🇬", "pool": "french"},
    "gabon":                {"name": "Gabon",                "flag": "🇬🇦", "pool": "french"},

    # East Asia
    "china":                {"name": "China",                "flag": "🇨🇳", "pool": "east_asian_chinese"},
    "north-korea":          {"name": "North Korea",          "flag": "🇰🇵", "pool": "east_asian_korean"},
    "south-korea":          {"name": "South Korea",          "flag": "🇰🇷", "pool": "east_asian_korean"},
    "mongolia":             {"name": "Mongolia",             "flag": "🇲🇳", "pool": "east_asian_mongolian"},
    "taiwan":               {"name": "Taiwan",               "flag": "🇹🇼", "pool": "east_asian_chinese"},

    # Southeast Asia
    "thailand":             {"name": "Thailand",             "flag": "🇹🇭", "pool": "southeast_asian_thai"},
    "vietnam":              {"name": "Vietnam",              "flag": "🇻🇳", "pool": "southeast_asian_vietnamese"},
    "laos":                 {"name": "Laos",                 "flag": "🇱🇦", "pool": "southeast_asian_thai"},
    "cambodia":             {"name": "Cambodia",             "flag": "🇰🇭", "pool": "southeast_asian_vietnamese"},
    "myanmar":              {"name": "Myanmar",              "flag": "🇲🇲", "pool": "southeast_asian_burmese"},
    "malaysia":             {"name": "Malaysia",             "flag": "🇲🇾", "pool": "southeast_asian_malay"},
    "singapore":            {"name": "Singapore",            "flag": "🇸🇬", "pool": "southeast_asian_malay"},
    "indonesia":            {"name": "Indonesia",            "flag": "🇮🇩", "pool": "southeast_asian_malay"},
    "philippines":          {"name": "Philippines",          "flag": "🇵🇭", "pool": "southeast_asian_filipino"},
    "brunei":               {"name": "Brunei",               "flag": "🇧🇳", "pool": "southeast_asian_malay"},
    "timor-leste":          {"name": "Timor-Leste",          "flag": "🇹🇱", "pool": "portuguese"},

    # South Asia
    "bhutan":               {"name": "Bhutan",               "flag": "🇧🇹", "pool": "south_asian_dzongkha"},
    "maldives":             {"name": "Maldives",             "flag": "🇲🇻", "pool": "south_asian_dhivehi"},

    # Central Asia & Caucasus
    "kazakhstan":           {"name": "Kazakhstan",           "flag": "🇰🇿", "pool": "central_asian"},
    "uzbekistan":           {"name": "Uzbekistan",           "flag": "🇺🇿", "pool": "central_asian"},
    "turkmenistan":         {"name": "Turkmenistan",         "flag": "🇹🇲", "pool": "central_asian"},
    "tajikistan":           {"name": "Tajikistan",           "flag": "🇹🇯", "pool": "central_asian"},
    "kyrgyzstan":           {"name": "Kyrgyzstan",           "flag": "🇰🇬", "pool": "central_asian"},
    "azerbaijan":           {"name": "Azerbaijan",           "flag": "🇦🇿", "pool": "caucasian"},
    "armenia":              {"name": "Armenia",              "flag": "🇦🇲", "pool": "caucasian"},
    "georgia":              {"name": "Georgia",              "flag": "🇬🇪", "pool": "caucasian"},

    # North America
    "canada":               {"name": "Canada",               "flag": "🇨🇦", "pool": "anglo_canadian"},
    "mexico":               {"name": "Mexico",               "flag": "🇲🇽", "pool": "iberian_latam"},

    # Central America
    "guatemala":            {"name": "Guatemala",            "flag": "🇬🇹", "pool": "iberian_latam"},
    "honduras":             {"name": "Honduras",             "flag": "🇭🇳", "pool": "iberian_latam"},
    "el-salvador":          {"name": "El Salvador",          "flag": "🇸🇻", "pool": "iberian_latam"},
    "nicaragua":            {"name": "Nicaragua",            "flag": "🇳🇮", "pool": "iberian_latam"},
    "costa-rica":           {"name": "Costa Rica",           "flag": "🇨🇷", "pool": "iberian_latam"},
    "panama":               {"name": "Panama",               "flag": "🇵🇦", "pool": "iberian_latam"},
    "belize":               {"name": "Belize",               "flag": "🇧🇿", "pool": "anglo_canadian"},

    # Caribbean
    "jamaica":              {"name": "Jamaica",              "flag": "🇯🇲", "pool": "caribbean"},
    "trinidad-and-tobago":  {"name": "Trinidad and Tobago",  "flag": "🇹🇹", "pool": "caribbean"},
    "barbados":             {"name": "Barbados",             "flag": "🇧🇧", "pool": "caribbean"},
    "bahamas":              {"name": "Bahamas",              "flag": "🇧🇸", "pool": "caribbean"},
    "cuba":                 {"name": "Cuba",                 "flag": "🇨🇺", "pool": "iberian_latam"},
    "dominican-republic":   {"name": "Dominican Republic",   "flag": "🇩🇴", "pool": "iberian_latam"},
    "haiti":                {"name": "Haiti",                "flag": "🇭🇹", "pool": "french"},
    "antigua-and-barbuda":  {"name": "Antigua and Barbuda",  "flag": "🇦🇬", "pool": "caribbean"},
    "dominica":             {"name": "Dominica",             "flag": "🇩🇲", "pool": "caribbean"},
    "grenada":              {"name": "Grenada",              "flag": "🇬🇩", "pool": "caribbean"},
    "saint-kitts-and-nevis":{"name": "Saint Kitts and Nevis","flag": "🇰🇳", "pool": "caribbean"},
    "saint-lucia":          {"name": "Saint Lucia",          "flag": "🇱🇨", "pool": "caribbean"},
    "saint-vincent-and-the-grenadines":{"name":"Saint Vincent and the Grenadines","flag":"🇻🇨","pool":"caribbean"},

    # South America
    "brazil":               {"name": "Brazil",               "flag": "🇧🇷", "pool": "portuguese_latam"},
    "argentina":            {"name": "Argentina",            "flag": "🇦🇷", "pool": "iberian_latam"},
    "chile":                {"name": "Chile",                "flag": "🇨🇱", "pool": "iberian_latam"},
    "uruguay":              {"name": "Uruguay",              "flag": "🇺🇾", "pool": "iberian_latam"},
    "paraguay":             {"name": "Paraguay",             "flag": "🇵🇾", "pool": "iberian_latam"},
    "bolivia":              {"name": "Bolivia",              "flag": "🇧🇴", "pool": "iberian_latam"},
    "peru":                 {"name": "Peru",                 "flag": "🇵🇪", "pool": "iberian_latam"},
    "ecuador":              {"name": "Ecuador",              "flag": "🇪🇨", "pool": "iberian_latam"},
    "colombia":             {"name": "Colombia",             "flag": "🇨🇴", "pool": "iberian_latam"},
    "venezuela":            {"name": "Venezuela",            "flag": "🇻🇪", "pool": "iberian_latam"},
    "guyana":               {"name": "Guyana",               "flag": "🇬🇾", "pool": "caribbean"},
    "suriname":             {"name": "Suriname",             "flag": "🇸🇷", "pool": "caribbean"},

    # Oceania
    "papua-new-guinea":     {"name": "Papua New Guinea",     "flag": "🇵🇬", "pool": "pacific_islander"},
    "fiji":                 {"name": "Fiji",                 "flag": "🇫🇯", "pool": "pacific_islander"},
    "solomon-islands":      {"name": "Solomon Islands",      "flag": "🇸🇧", "pool": "pacific_islander"},
    "vanuatu":              {"name": "Vanuatu",              "flag": "🇻🇺", "pool": "pacific_islander"},
    "samoa":                {"name": "Samoa",                "flag": "🇼🇸", "pool": "pacific_islander"},
    "tonga":                {"name": "Tonga",                "flag": "🇹🇴", "pool": "pacific_islander"},
    "kiribati":             {"name": "Kiribati",             "flag": "🇰🇮", "pool": "pacific_islander"},
    "tuvalu":               {"name": "Tuvalu",               "flag": "🇹🇻", "pool": "pacific_islander"},
    "nauru":                {"name": "Nauru",                "flag": "🇳🇷", "pool": "pacific_islander"},
    "palau":                {"name": "Palau",                "flag": "🇵🇼", "pool": "pacific_islander"},
    "marshall-islands":     {"name": "Marshall Islands",     "flag": "🇲🇭", "pool": "pacific_islander"},
    "micronesia":           {"name": "Micronesia",           "flag": "🇫🇲", "pool": "pacific_islander"},
}


# 33-player squad template:
# 1: captain (RH bat, anchor)
# 2: vice-captain (RH bat, opener)
# 3: keeper (RH bat, finisher)
# 4: keeper (RH bat, anchor)
# 5: keeper-reserve (LH bat, finisher)
# 6-14: 9 specialist batsmen (mix RH/LH, mix archetypes)
# 15-18: 4 all-rounders
# 19-26: 8 pace bowlers
# 27-33: 7 spinners
SQUAD_TEMPLATE = [
    # (role, batting_hand, bowling_style, batting_archetype, bowling_archetype)
    ("captain",          "RH", None,           "anchor",        None),
    ("vice-captain",     "RH", None,           "opener",        None),
    ("keeper",           "RH", None,           "finisher",      None),
    ("keeper",           "RH", None,           "anchor",        None),
    ("keeper-reserve",   "LH", None,           "finisher",      None),
    ("batsman",          "RH", None,           "opener",        None),
    ("batsman",          "LH", None,           "opener",        None),
    ("batsman",          "RH", None,           "power-hitter",  None),
    ("batsman",          "LH", None,           "power-hitter",  None),
    ("batsman",          "RH", None,           "anchor",        None),
    ("batsman",          "RH", None,           "finisher",      None),
    ("batsman",          "LH", None,           "anchor",        None),
    ("batsman",          "RH", None,           "opener",        None),
    ("batsman",          "LH", None,           "finisher",      None),
    ("all-rounder",      "RH", "RA pace",      "all-rounder",   "pace"),
    ("all-rounder",      "LH", "LA pace",      "all-rounder",   "pace"),
    ("all-rounder",      "RH", "RA off-spin",  "all-rounder",   "off-spin"),
    ("all-rounder",      "LH", "RA leg-spin",  "all-rounder",   "leg-spin"),
    ("bowler",           None, "RA pace",      "tail-ender",    "pace"),
    ("bowler",           None, "LA pace",      "tail-ender",    "pace"),
    ("bowler",           None, "RA swing",     "tail-ender",    "swing"),
    ("bowler",           None, "RA pace",      "tail-ender",    "pace"),
    ("bowler",           None, "RA pace",      "tail-ender",    "pace"),
    ("bowler",           None, "LA pace",      "tail-ender",    "pace"),
    ("bowler",           None, "RA mystery",   "tail-ender",    "mystery"),
    ("bowler",           None, "RA pace",      "tail-ender",    "pace"),
    ("bowler",           None, "RA off-spin",  "tail-ender",    "off-spin"),
    ("bowler",           None, "RA leg-spin",  "tail-ender",    "leg-spin"),
    ("bowler",           None, "LA off-spin",  "tail-ender",    "off-spin"),
    ("bowler",           None, "RA leg-spin",  "tail-ender",    "leg-spin"),
    ("bowler",           None, "RA off-spin",  "tail-ender",    "off-spin"),
    ("bowler",           None, "LA mystery",   "tail-ender",    "mystery"),
    ("bowler",           None, "RA off-spin",  "tail-ender",    "off-spin"),
]


def _format_name(given: str, family: str, convention: str) -> str:
    return f"{given} {family}" if convention == "given-family" else f"{family} {given}"


def _generate_unique_names(pool: dict, n: int, rng: random.Random) -> list[str]:
    """Sample n unique given+family combos from a pool, preserving naming convention."""
    given_pool = pool["given"]
    family_pool = pool["family"]
    convention = pool["convention"]
    names: list[str] = []
    seen: set[str] = set()
    safety = 0
    while len(names) < n and safety < n * 50:
        safety += 1
        g = rng.choice(given_pool)
        f = rng.choice(family_pool)
        formatted = _format_name(g, f, convention)
        if formatted in seen:
            continue
        seen.add(formatted)
        names.append(formatted)
    if len(names) < n:
        # Pool too small for unique combos — pad with numbered suffixes
        i = 1
        while len(names) < n:
            base = _format_name(rng.choice(given_pool), rng.choice(family_pool), convention)
            candidate = f"{base} #{i}"
            if candidate not in seen:
                seen.add(candidate)
                names.append(candidate)
            i += 1
    return names


def generate_country(slug: str, info: dict, *, seed: int | None = None) -> dict:
    pool_key = info["pool"]
    pool = POOLS[pool_key]
    rng = random.Random(seed if seed is not None else hash(slug) & 0xFFFFFFFF)

    # 33 player names + 2 staff names
    names = _generate_unique_names(pool, 35, rng)
    player_names = names[:33]
    staff_names = names[33:35]

    players = []
    for i, ((role, bat_hand, bowl_style, bat_arch, bowl_arch), name) in enumerate(zip(SQUAD_TEMPLATE, player_names), start=1):
        players.append({
            "id": i,
            "name": name,
            "role": role,
            "batting_hand": bat_hand,
            "bowling_style": bowl_style,
            "batting_archetype": bat_arch,
            "bowling_archetype": bowl_arch,
        })

    staff = [
        {"role": "coach", "name": staff_names[0]},
        {"role": "assistant_coach", "name": staff_names[1]},
    ]

    return {
        "country": info["name"],
        "flag": info["flag"],
        "naming_convention": pool["convention"],
        "players": players,
        "staff": staff,
    }


def main() -> None:
    skipped: list[str] = []
    written: list[str] = []
    for slug, info in COUNTRIES.items():
        out_path = REPO_DATA / f"{slug}.json"
        if out_path.exists():
            skipped.append(slug)
            continue
        roster = generate_country(slug, info)
        out_path.write_text(json.dumps(roster, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(slug)
    print(f"Generated {len(written)} new rosters; skipped {len(skipped)} existing.")
    if "--verbose" in sys.argv:
        for s in written:
            print(f"  + {s}")
        for s in skipped:
            print(f"  · {s}")


if __name__ == "__main__":
    main()
