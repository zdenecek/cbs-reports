
-- Table: _PostupTrid
CREATE TABLE _PostupTrid (
    Datum datetime NOT NULL,
    IdHrace int NOT NULL,
    IdTridy int NOT NULL,
    IdTurnaje int NULL,
    IdTridyPuv int NULL
);

ALTER TABLE _PostupTrid ADD PRIMARY KEY (Datum);
ALTER TABLE _PostupTrid ADD PRIMARY KEY (IdHrace);

-- Table: _ZiskHrace
CREATE TABLE _ZiskHrace (
    IdHrace int NOT NULL,
    IdSezony int NOT NULL,
    PocetKB int NOT NULL,
    Clenstvi char(1) NOT NULL
);

ALTER TABLE _ZiskHrace ADD PRIMARY KEY (IdHrace);
ALTER TABLE _ZiskHrace ADD PRIMARY KEY (IdSezony);

-- Table: Hrac
CREATE TABLE Hrac (
    Legitimace int identity NOT NULL,
    Prijmeni varchar(50) NOT NULL,
    Jmena varchar(50) NOT NULL,
    Rocnik int NULL,
    PohlaviM bit NOT NULL,
    IdKlubu int NOT NULL,
    ClenstviOd datetime NOT NULL,
    ClenstviDo datetime NULL,
    PrenosKB int NOT NULL,
    PrenosPopis varchar(100) NULL,
    Mail varchar(100) NULL,
    Telefon varchar(50) NULL,
    Adresa varchar(100) NULL,
    Foto varchar(200) NULL,
    IdUzivatele int NULL,
    _AktualniKB int NOT NULL,
    _AktualniTrida int NOT NULL,
    Poznamka varchar(300) NULL,
    Funkce int NOT NULL,
    DatumNarozeni datetime NULL
);

ALTER TABLE Hrac ADD PRIMARY KEY (Legitimace);
CREATE INDEX IDX_Hrac_klub ON Hrac(IdKlubu);
CREATE INDEX IDX_Hrac_Nazev ON Hrac(Prijmeni);
CREATE INDEX IDX_Hrac_Nazev ON Hrac(Jmena);
CREATE INDEX IDX_Hrac_AktKB ON Hrac(_AktualniKB);

-- Table: KategorieTurnaje
CREATE TABLE KategorieTurnaje (
    Id int identity NOT NULL,
    IdSezony int NOT NULL,
    Nazev varchar(200) NOT NULL,
    ProcentoHracu int NULL,
    VkladSB decimal(5,2) NULL,
    ProcentoBonifikace int NULL,
    NasobekKB smallint NULL
);

ALTER TABLE KategorieTurnaje ADD PRIMARY KEY (Id);

-- Table: Klub
CREATE TABLE Klub (
    Id int identity NOT NULL,
    Nazev varchar(100) NOT NULL,
    Zkratka char(3) NULL,
    Adresa varchar(200) NULL,
    Mail varchar(100) NULL,
    Web varchar(200) NULL,
    Telefon varchar(50) NULL,
    IdPredsedy int NULL,
    PopisHrani varchar(300) NULL,
    Status varchar(100) NULL,
    Stanovy varchar(200) NULL
);

ALTER TABLE Klub ADD PRIMARY KEY (Id);

-- Table: KvocientyKB
CREATE TABLE KvocientyKB (
    PocetUcastniku int NOT NULL,
    Kvocient real NULL
);

ALTER TABLE KvocientyKB ADD PRIMARY KEY (PocetUcastniku);

-- Table: Prihlaseny
CREATE TABLE Prihlaseny (
    Id int identity NOT NULL,
    IdPrihlasky int NOT NULL,
    Nazev varchar(200) NULL,
    DatumPrihlaseni datetime NOT NULL
);

ALTER TABLE Prihlaseny ADD PRIMARY KEY (Id);
CREATE INDEX IDX_Prihlaseny_IdPrihlasky ON Prihlaseny(IdPrihlasky);

-- Table: Prihlaska
CREATE TABLE Prihlaska (
    Id int identity NOT NULL,
    Nazev varchar(100) NULL,
    Popis varchar(500) NULL,
    Misto varchar(50) NULL,
    DatumOd datetime NOT NULL,
    DatumDo datetime NOT NULL,
    Stav smallint NOT NULL,
    IdKlubu int NOT NULL,
    Vedouci varchar(50) NULL,
    TypTurnaje smallint NOT NULL,
    Web varchar(200) NULL,
    Mail varchar(100) NULL,
    Kontakty varchar(200) NULL,
    _PocetPrihlasenych int NOT NULL,
    Vklad smallmoney NOT NULL,
    SlevaClenR smallmoney NULL,
    SlevaClenS smallmoney NULL,
    SlevaVekK smallmoney NULL,
    SlevaVekY smallmoney NULL,
    SlevaVekJ smallmoney NULL,
    SlevaVekS smallmoney NULL,
    SlevaVcas smallmoney NULL,
    DatumVcas datetime NULL,
    IdTurnaje int NULL,
    IdUzivatele int NOT NULL,
    IdKategorie int NULL,
    _IdSezony int NULL
);

ALTER TABLE Prihlaska ADD PRIMARY KEY (Id);

-- Table: PrihlUcast
CREATE TABLE PrihlUcast (
    Id int identity NOT NULL,
    IdPrihlaseneho int NOT NULL,
    IdHrace int NULL,
    Nazev varchar(200) NULL
);

ALTER TABLE PrihlUcast ADD PRIMARY KEY (Id);
CREATE INDEX IDX_PrihlUcast_IdPrihlaseneho ON PrihlUcast(IdPrihlaseneho);

-- Table: Prispevek
CREATE TABLE Prispevek (
    Id int identity NOT NULL,
    IdHrace int NOT NULL,
    IdSezony int NOT NULL,
    Datum datetime NOT NULL,
    Kc smallmoney NOT NULL,
    Clenstvi char(1) NOT NULL,
    IdUzivatele int NOT NULL,
    _Od datetime NULL,
    _Do datetime NULL
);

ALTER TABLE Prispevek ADD PRIMARY KEY (Id);
CREATE INDEX IDX_Prispevek_HracSezona ON Prispevek(IdHrace);
CREATE INDEX IDX_Prispevek_HracSezona ON Prispevek(IdSezony);

-- Table: Serie
CREATE TABLE Serie (
    Id int identity NOT NULL,
    IdSezony int NOT NULL,
    Nazev varchar(200) NOT NULL,
    Ucast0KB int NULL,
    Ucast0SB decimal(5,2) NULL,
    Ucast1KB int NULL,
    Ucast1SB decimal(5,2) NULL,
    StavOtevrena bit NULL
);

ALTER TABLE Serie ADD PRIMARY KEY (Id);

-- Table: SerieTurnaje
CREATE TABLE SerieTurnaje (
    IdSerie int NOT NULL,
    IdTurnaje int NOT NULL
);

ALTER TABLE SerieTurnaje ADD PRIMARY KEY (IdSerie);
ALTER TABLE SerieTurnaje ADD PRIMARY KEY (IdTurnaje);

-- Table: Sezona
CREATE TABLE Sezona (
    Id int NOT NULL,
    Od datetime NOT NULL,
    Do datetime NOT NULL,
    TypKR int NOT NULL,
    StavOtevrena bit NOT NULL,
    PrispevekR smallmoney NULL,
    PrispevekS smallmoney NULL,
    PrispevekRJ smallmoney NULL,
    PrispevekSJ smallmoney NULL,
    PrispevekK smallmoney NULL,
    Procento1 int NULL,
    BonusSB1 int NULL,
    Procento2 int NULL,
    BonusSB2 int NULL,
    PresahClenstvi datetime NULL,
    VekK int NULL
);

ALTER TABLE Sezona ADD PRIMARY KEY (Id);

-- Table: Soutezici
CREATE TABLE Soutezici (
    Id int identity NOT NULL,
    IdTurnaje int NOT NULL,
    Nazev varchar(200) NULL,
    Vysledek varchar(100) NULL,
    PoradiOd int NOT NULL,
    PoradiDo int NOT NULL,
    KB int NOT NULL,
    SB decimal(5,2) NOT NULL
);

ALTER TABLE Soutezici ADD PRIMARY KEY (Id);
CREATE INDEX IDX_Soutezici_TurnajPoradi ON Soutezici(IdTurnaje);
CREATE INDEX IDX_Soutezici_TurnajPoradi ON Soutezici(PoradiOd);

-- Table: Turnaj
CREATE TABLE Turnaj (
    Id int identity NOT NULL,
    Nazev varchar(100) NULL,
    Misto varchar(50) NULL,
    DatumOd datetime NOT NULL,
    DatumDo datetime NOT NULL,
    _IdSezony int NULL,
    IdKlubu int NULL,
    Vedouci varchar(50) NULL,
    TypTurnaje smallint NOT NULL,
    IdKategorie int NULL,
    PocetRozdani int NULL,
    _PocetSoutezicich int NOT NULL,
    IdUzivatele int NOT NULL,
    Dokumentace varchar(200) NULL
);

ALTER TABLE Turnaj ADD PRIMARY KEY (Id);
CREATE INDEX IDX_Turnaj_SezonaSoutez ON Turnaj(_IdSezony);
CREATE INDEX IDX_Turnaj_SezonaSoutez ON Turnaj(IdKategorie);

-- Table: TypTurnaje
CREATE TABLE TypTurnaje (
    Id smallint NOT NULL,
    Nazev varchar(100) NULL
);

ALTER TABLE TypTurnaje ADD PRIMARY KEY (Id);

-- Table: Ucast
CREATE TABLE Ucast (
    IdSouteziciho int NOT NULL,
    IdHrace int NOT NULL,
    PocetRozdani int NULL,
    _KB int NOT NULL,
    _SB decimal(5,2) NOT NULL,
    _IdSezony int NULL,
    _IdKategorie int NULL,
    _Clenstvi char(1) NULL
);

ALTER TABLE Ucast ADD PRIMARY KEY (IdSouteziciho);
ALTER TABLE Ucast ADD PRIMARY KEY (IdHrace);
CREATE INDEX IDX_Ucast_SezonaHrac ON Ucast(_IdSezony);
CREATE INDEX IDX_Ucast_SezonaHrac ON Ucast(IdHrace);
CREATE INDEX IDX_Ucast_RegSoutez ON Ucast(_IdKategorie);
CREATE INDEX IDX_Ucast_HracSoutezBody ON Ucast(IdHrace);
CREATE INDEX IDX_Ucast_HracSoutezBody ON Ucast(IdSouteziciho);
CREATE INDEX IDX_Ucast_HracSoutezBody ON Ucast(_KB);
CREATE INDEX IDX_Ucast_HracSoutezBody ON Ucast(_SB);

-- Table: Uzivatel
CREATE TABLE Uzivatel (
    Id int identity NOT NULL,
    Nazev varchar(50) NOT NULL,
    Login varchar(50) NULL,
    HashPwd varchar(50) NULL,
    Role int NOT NULL,
    IdHrace int NULL,
    Mail varchar(50) NULL,
    Telefon varchar(50) NULL
);

ALTER TABLE Uzivatel ADD PRIMARY KEY (Id);

-- Table: Voucher
CREATE TABLE Voucher (
    Id int identity NOT NULL,
    IdHrace int NOT NULL,
    IdTurnajZisk int NULL,
    Procento smallint NOT NULL,
    Platnost datetime NOT NULL,
    IdTurnajUplatnen int NULL,
    IdUzivatele int NOT NULL,
    Nazev varchar(150) NULL
);

ALTER TABLE Voucher ADD PRIMARY KEY (Id);

-- Table: VykonnostniTrida
CREATE TABLE VykonnostniTrida (
    Id int identity NOT NULL,
    Nazev varchar(50) NOT NULL,
    MinKB int NOT NULL,
    _MaxKB int NOT NULL
);

ALTER TABLE VykonnostniTrida ADD PRIMARY KEY (Id);

-- Table: trace_xe_action_map
CREATE TABLE trace_xe_action_map (
    trace_column_id smallint NOT NULL,
    package_name nvarchar(60) NOT NULL,
    xe_action_name nvarchar(60) NOT NULL
);


-- Table: trace_xe_event_map
CREATE TABLE trace_xe_event_map (
    trace_event_id smallint NOT NULL,
    package_name nvarchar(60) NOT NULL,
    xe_event_name nvarchar(60) NOT NULL
);


-- View: vRanking


CREATE VIEW [dbo].[vRanking]
AS
SELECT        row_number() OVER (ORDER BY _AktualniKB DESC) AS Poradi, *, Prijmeni + ' ' + Jmena AS Jmeno
FROM            (SELECT        Legitimace, Prijmeni, Jmena, Rocnik, PohlaviM, IdKlubu, k.Zkratka AS ZkratkaKlubu, h._AktualniTrida, t .Nazev AS Trida, h.Mail, dbo.GetClenstvi(Legitimace, getdate()) AS Clenstvi, dbo.GetKategorieHrace(Rocnik, 
                                                    PohlaviM, getdate()) AS Kategorie, hh._AktualniKB
                          FROM            (SELECT        h.Legitimace AS Leg, sum(cast(CASE WHEN t .DatumDo <= DATEADD(year, - 2, getdate()) THEN (u._KB + u._SB * 1000) / 3 WHEN t .DatumDo <= DATEADD(year, - 1, getdate()) THEN (u._KB + u._SB * 1000)
                                                                               * 2 / 3 ELSE (u._KB + u._SB * 1000) END + 0.5 AS int)) AS _AktualniKB
                                                    FROM            Hrac h INNER JOIN
                                                                              Ucast u ON u.IdHrace = h.Legitimace LEFT JOIN
                                                                              Soutezici s ON s.Id = u.IdSouteziciho LEFT JOIN
                                                                              Turnaj t ON t .Id = s.IdTurnaje
                                                    WHERE        t .DatumDo BETWEEN DATEADD(day, 1, DATEADD(year, - 3, getdate())) AND getdate() AND t .IdKategorie IN
                                                                                  (SELECT        Id
                                                                                    FROM            KategorieTurnaje
                                                                                    WHERE        VkladSB > 0)
                                                    GROUP BY h.Legitimace) hh INNER JOIN
                                                    Hrac h ON h.Legitimace = hh.Leg LEFT JOIN
                                                    Klub k ON k.Id = h.IdKlubu INNER JOIN
                                                    VykonnostniTrida t ON t .Id = h._AktualniTrida) x
WHERE        _AktualniKB > 0 AND Clenstvi in ('S', 'R');;



