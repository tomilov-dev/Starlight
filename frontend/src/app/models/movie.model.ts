import { IMDbMovieBase } from './base.movie.model';
import { Country } from './country.model';
import { Genre } from './genre.model';
import { MoviePrincipalPerson } from './person.model';

export interface MovieType {
  id: number;
  name_en: string;
  name_ru: string;
}

export interface MovieCollection {
  id: number;
  tmdb_id: number;

  name_en: string;
  name_ru: string | null;
  image_url: string | null;
}

export interface TMDbMovie {
  id: number;
  tmdb_mvid: number;

  release_date: Date;
  budget: number | null;
  revenue: number | null;
  image_url: string | null;

  tagline_en: string | null;
  overview_en: string | null;

  tagline_ru: string | null;
  overview_ru: string | null;

  rate: number | null;
  votes: number | null;
  popularity: number | null;

  collection: MovieCollection | null;
}

export interface MovieCountry {
  id: number;
  country: Country;
}

export interface ProductionCompany {
  id: number;
  tmdb_id: number;

  name_en: string;
  slug: string;
  image_url: string | null;

  country_origin: Country;
}

export interface MovieProduction {
  id: number;
  production_company: ProductionCompany;
}

export interface MovieGenre {
  id: number;
  genre: Genre;
}

export interface IMDbMovieExtended extends IMDbMovieBase {
  tmdb: TMDbMovie | null;
  genres: MovieGenre[];
  countries: MovieCountry[];
  production_companies: MovieProduction[];
  principals: MoviePrincipalPerson[];
}
