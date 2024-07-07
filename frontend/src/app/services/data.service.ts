import { Injectable } from '@angular/core';
import { Genre } from '../models/genre.model';
import { Country } from '../models/country.model';
import { IMDbMovieExtended } from '../models/movie.model';
import { ApiService } from './api.service';
import { Observable } from 'rxjs';
import { IMDbPersonBase, IMDbPersonExtended } from '../models/person.model';
import { IMDbMovieBase } from '../models/base.movie.model';

@Injectable({
  providedIn: 'root',
})
export class DataService {
  private genres: Genre[] = [];
  private genresMapper: Map<string, Genre> = new Map();

  private countries: Country[] = [];
  private countriesMapper: Map<number, Country> = new Map();

  constructor(private api: ApiService) {}

  setGenres(genres: Genre[]): void {
    this.genres = genres;
    this.genresMapper = new Map(genres.map((genre) => [genre.slug, genre]));
  }

  getGenres(): Genre[] {
    return this.genres;
  }

  getGenre(slug: string): Genre | undefined {
    return this.genresMapper.get(slug);
  }

  setCountries(countries: Country[]): void {
    this.countries = countries;
    this.countriesMapper = new Map(
      countries.map((country) => [country.id, country])
    );
  }

  getCountries(): Country[] {
    return this.countries;
  }

  getCountry(countryId: number): Country | undefined {
    return this.countriesMapper.get(countryId);
  }

  getMovie(slug: string): Observable<IMDbMovieExtended> {
    return this.api.getMovie(slug);
  }

  getPerson(slug: string): Observable<IMDbPersonExtended> {
    return this.api.getPerson(slug);
  }

  searchMovies(searchQuery: string): Observable<IMDbMovieBase[]> {
    return this.api.searchMovies(searchQuery);
  }

  searchPersons(searchQuery: string): Observable<IMDbPersonBase[]> {
    return this.api.searchPersons(searchQuery);
  }

  getMoviesByGenre(
    slug: string,
    page: number,
    pageSize: number
  ): Observable<IMDbMovieBase[]> {
    return this.api.getMoviesByGenre(slug, page, pageSize);
  }
}
