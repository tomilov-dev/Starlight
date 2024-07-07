import { IMDbMovieBase } from './base.movie.model';

export interface IMDbPersonBase {
  id: number;

  imdb_nmid: string;
  name_en: string;
  slug: string;

  birth_y: number | null;
  death_y: number | null;
  image_url: string | null;

  tmdb_added: boolean;
  imdb_extra_added: boolean;
}

export interface Profession {
  id: number;
  imdb_name: string;
  name_en: string;
  name_ru: string;
}

export interface PersonProfession {
  id: number;
  profession: Profession;
}

export interface MoviePrincipal {
  id: number;
  ordering: number;
  job: string | null;
  characters: string[];
}

export interface MoviePrincipalMovie extends MoviePrincipal {
  imdb_movie: IMDbMovieBase;
}

export interface MoviePrincipalPerson extends MoviePrincipal {
  imdb_person: IMDbPersonBase;
}

export interface TMDbPerson {
  id: number;
  tmdb_nmid: number;

  name_en: string;
  name_ru: string | null;

  gender: number;
}

export interface IMDbPersonExtended extends IMDbPersonBase {
  tmdb: TMDbPerson;
  professions: PersonProfession[];
  movies: MoviePrincipalMovie[];
}
