import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HomePageComponent } from './home-page/home-page.component';
import { ComponentsModule } from '../components/components.module';
import { GenresComponent } from './genres/genres.component';
import { SearchComponent } from './search/search.component';
import { RouterModule } from '@angular/router';
import { GenreMoviesComponent } from './genre-movies/genre-movies.component';
import { MovieComponent } from './movie/movie.component';
import { SelectionComponent } from './selection/selection.component';
import { FormsModule } from '@angular/forms';
import { PersonComponent } from './person/person.component';
import { SvgModule } from '../svg/svg.module';

@NgModule({
  declarations: [
    HomePageComponent,
    GenresComponent,
    SearchComponent,
    GenreMoviesComponent,
    MovieComponent,
    SelectionComponent,
    PersonComponent,
  ],
  imports: [
    CommonModule,
    ComponentsModule,
    RouterModule,
    FormsModule,
    SvgModule,
  ],
  exports: [
    HomePageComponent,
    GenresComponent,
    SearchComponent,
    GenreMoviesComponent,
    MovieComponent,
    SelectionComponent,
    PersonComponent,
  ],
})
export class PagesModule {}
